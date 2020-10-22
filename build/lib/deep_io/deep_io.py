from hyperpeer import Peer, PeerState
import asyncio
import subprocess
import ssl
import logging
import os
import inspect

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
    stream_manager_id (str): ID of the remote peer. If specified it will specifically connect to that peer.
    auto_connect (bool): If true it will automatically connect with the first stream_manager peer available otherwise it will wait for remote connections. Default `False`.

    """    
    def __init__(self, server_address, server_port, source, peer_id, peer_type='stream_capture', format=None, metadata=None, stream_manager_id=None, auto_connect=False, remotePeerId=None):
        self.id = peer_id
        self.metadata = metadata
        self.stream_manager_id = stream_manager_id
        self.remotePeerId = remotePeerId
        if auto_connect:
            self.remotePeerType = 'stream_manager'
        else:
            self.remotePeerType = None
        
        self._frame_handlers = []
        def frame_consumer(frame):
            for handler in self._frame_handlers:
                handler(frame)

        self.peer = Peer(f'wss://{server_address}:{server_port}', id=peer_id, peer_type=peer_type, frame_consumer=frame_consumer,
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
        handler (function|coroutine): A function or asyncio coroutine that will be called with the data object. 
        """
        self.peer.add_data_handler(handler)

    def add_frame_handler(self, handler):
        """
        Adds a function to the list of handlers to call whenever a frame is received.

        # Arguments
        handler (function): A function that will be called with the last received frame. 
        """
        self._frame_handlers.append(handler)

    def send_metadata(self, metadata):
        """
        Send the new metadata to the connected remote peer.

        # Arguments
        metadata (str|dict): String or dictionary that describes the video source and its attributes.

        # Returns
        asyncio.Task: Sending task.
        """        
        return asyncio.create_task(self.peer.send({'type': 'metadata', 'metadata': metadata}))

    async def start(self):
        await self.peer.open()
        self.peer.add_data_handler(self._on_data)
        try:
            while True:
                if self.stream_manager_id:
                    await self.peer.connect_to(self.stream_manager_id)
                    logging.info(f'connected to %s', self.stream_manager_id)
                elif self.remotePeerType:
                    # List connected peers
                    peers = await self.peer.get_peers()
                    for peer in peers:
                        if peer['type'] == self.remotePeerType and not peer['busy']:
                            await self.peer.connect_to(peer['id'])
                            self.stream_manager_id = peer['id']
                            logging.info(f'connected to {self.remotePeerType} with id: {self.stream_manager_id}')
                            if self.remotePeerId:
                                await self.peer.send({'type': 'source', 'peerId': self.remotePeerId})
                            else:
                                await self.peer.send({'type': 'source', 'peerId': self.id})
                            break
                    if self.stream_manager_id == None:
                        await asyncio.sleep(1)
                        continue
                else:
                    logging.info(f'[{self.id}]: Waiting peer connections...')
                    self.stream_manager_id = await self.peer.listen_connections()
                    logging.info(f'[{self.id}]: Connection request from peer: {self.stream_manager_id}')
                    await self.peer.accept_connection()
                await self.peer.send({'type': 'metadata', 'metadata': self.metadata})
                while self.peer.readyState != PeerState.ONLINE:
                    await asyncio.sleep(1)
                await asyncio.sleep(1)
                self.stream_manager_id = None
        except Exception as err:
            logging.error(f'[{self.id}]: Execution error: {err}')
            await self.peer.close()
            raise err
        
    
    async def stop(self):
        await self.peer.close()

    def run(self):
        """
        Start the event loop of the DeepIO application
        """
        if self.running:
            return
        self.running = True
        # run event loop
        try:
            loop = asyncio.get_event_loop()
        except:
            loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(self.start())
            #asyncio.run(asyncio.gather(demo1.start(), demo2.start()))
        except KeyboardInterrupt:
            logging.info(' -> End signal')
        finally:
            # cleanup
            logging.info(' -> Cleaning...')
            loop.run_until_complete(self.stop())

