# DEEP-IO-PY 
deep-io-py is the python module that provides the interface to communicate with the backend or core components of real-time computer vision applications based on the [**DEEP-Framework**](https://github.com/crs4/deep_framework). This module provides a class called [DeepIO](#DeepIO) which manages the streaming of video and data to and from the application core. 

# Features

 - Built on top of Python’s standard asynchronous I/O framework [**asyncio**](https://docs.python.org/3/library/asyncio.html?highlight=asyncio#module-asyncio), and [**hyperpeer-py**](https://github.com/crs4/hyperpeer-py) . 
 

# API Reference


# DeepIO
```python
DeepIO(self, server_address, server_port, source, peer_id, peer_type='stream_capture', format=None, metadata=None, remotePeerId=None, auto_connect=False)
```

The DeepIO class represents the WebRTC-based connection between the local application and the remote DEEP_Framework processing core.

__Arguments__

- __server_address (str)__: URL or IP of the DEEP_Framework server.
- __server_port (str)__: Port of the DEEP_Framework server.
- __source (str)__: URL or path of the video source.
- __peer_id (str)__: Peer unique identification string. Must be unique among all connected peers. It can be used by other clients to find and connect to this peer.
- __peer_type (str)__: Peer type. It's used by other peers to know the role of the peer in the current application. Default 'stream_capture'.
- __format (str)__: Format of the video source. Defaults to autodetect.
- __metadata (str|dict)__: String or dictionary that describes the video source and its attributes.
- __remotePeerId (str)__: ID of the remote peer. If specified it will specifically connect to that peer.
- __auto_connect (bool)__: If true it will automatically connect with the first stream_manager peer available otherwise it will wait for remote connections. Default `False`.


## add_data_handler
```python
DeepIO.add_data_handler(self, handler)
```

Adds a function to the list of handlers to call whenever data is received.

__Arguments__

- __handler (function)__: A function that will be called with the an argument called 'data'.

## send_metadata
```python
DeepIO.send_metadata(self, metadata)
```

Send the new metadata to the connected remote peer.

Args:
    metadata (str|dict): String or dictionary that describes the video source and its attributes.

Returns:
    asyncio.Task: Sending task.

## run
```python
DeepIO.run(self)
```

Start the event loop of the DeepIO application

