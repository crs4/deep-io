from hyperpeer import Peer, PeerState
import asyncio
import subprocess
import ssl
import logging
import os

ROOT = os.path.dirname(__file__)
logging.basicConfig(level=logging.INFO)

#ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
#ssl_context.load_verify_locations('cert.pem')

ssl_context = ssl.create_default_context()
ssl_context.options |= ssl.OP_ALL
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE


class DeepIO:
    def __init__(self, server_address, server_port, source, peer_id, peer_type, format=None, metadata=None, remotePeerId=None, remotePeerType=None):
        self.id = peer_id
        self.metadata = metadata
        self.remotePeerId = remotePeerId
        self.remotePeerType = remotePeerType
        self.peer = Peer(f'wss://{server_address}:{server_port}', id=peer_id, peer_type=peer_type, 
                        media_source=source, ssl_context=ssl_context, media_source_format=format)
        self.running = False

    async def _on_data(self, data):
        # logging.info(f'[{self.id}]: Remote message: {str(data)}')
        if data['type'] == 'data':
            acknowledge = {
                'type': 'acknowledge',
                'rec_time': data['rec_time']
            }
            await self.peer.send(acknowledge)
    
    def add_data_handler(self, handler):
        self.peer.add_data_handler(handler)

    def send_metadata(self, metadata):
        return asyncio.create_task(self.peer.send({'type': 'metadata', 'metadata': metadata}))

    async def _start(self):
        await self.peer.open()
        self.peer.add_data_handler(self._on_data)
        try:
            while True:
                if self.remotePeerId:
                    await self.peer.connect_to(self.remotePeerId)
                    logging.info(f'connected to %s', self.remotePeerId)
                elif self.remotePeerType:
                    # List connected peers
                    peers = await self.peer.get_peers()
                    for peer in peers:
                        if peer['type'] == self.remotePeerType and not peer['busy']:
                            await self.peer.connect_to(peer['id'])
                            logging.info(f'connected to {self.remotePeerType} with id: {self.remotePeerId}')
                            await self.peer.send({'type': 'source', 'peerId': self.id})
                            break
                else:
                    logging.info(f'[{self.id}]: Waiting peer connections...')
                    self.remotePeerId = await self.peer.listen_connections()
                    logging.info(f'[{self.id}]: Connection request from peer: {self.remotePeerId}')
                    await self.peer.accept_connection()
                await self.peer.send({'type': 'metadata', 'metadata': self.metadata})
                while self.peer.readyState != PeerState.ONLINE:
                    await asyncio.sleep(1)
                await asyncio.sleep(1)
                self.remotePeerId = None
        except Exception as err:
            logging.error(f'[{self.id}]: Execution error: {err}')
            #raise err
        finally:
            await self.peer.close()
    
    async def _stop(self):
        await self.peer.close()

    def run(self):
        if self.running:
            return
        self.running = True
        # run event loop
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self._start())
            #asyncio.run(asyncio.gather(demo1._start(), demo2._start()))
        except KeyboardInterrupt:
            logging.info(' -> End signal')
        finally:
            # cleanup
            logging.info(' -> Cleaning...')
            loop.run_until_complete(self._stop())

