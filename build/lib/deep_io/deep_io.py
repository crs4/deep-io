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
    """
    The DeepIO class represents the WebRTC-based connection between the local application and the remote DEEP_Framework processing core.

    # Arguments
    server_address (str): URL or IP of the DEEP_Framework server.
    server_port (str): Port of the DEEP_Framework server.
    source (str): URL or path of the video source.
    peer_id (str): Peer unique identification string. Must be unique among all connected peers. It can be used by other clients to find and connect to this peer. 
    peer_type (str): Peer type. It's used by other peers to know the role of the peer in the current application. Default 'stream_capture'.
    format (str): Format of the video source. Defaults to autodetect.
    metadata (str|dict): String or dictionary that describes the video source and its attributes.
    remotePeerId (str): ID of the remote peer. If specified it will specifically connect to that peer.
    auto_connect (bool): If true it will automatically connect with the first stream_manager peer available otherwise it will wait for remote connections. Default `False`.

    """    
    def __init__(self, server_address, server_port, source, peer_id, peer_type='stream_capture', format=None, metadata=None, remotePeerId=None, auto_connect=False):
        self.id = peer_id
        self.metadata = metadata
        self.remotePeerId = remotePeerId
        if auto_connect:
            self.remotePeerType = 'stream_manager'
        else:
            self.remotePeerType = None

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
        """
        Adds a function to the list of handlers to call whenever data is received.

        # Arguments
        handler (function): A function that will be called with the an argument called 'data'. 
        """
        self.peer.add_data_handler(handler)

    def send_metadata(self, metadata):
        """
        Send the new metadata to the connected remote peer.

        Args:
            metadata (str|dict): String or dictionary that describes the video source and its attributes.

        Returns:
            asyncio.Task: Sending task.
        """        
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
        """
        Start the event loop of the DeepIO application
        """
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

