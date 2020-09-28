#!/bin/sh
intro="
# DEEP-IO-PY
\ndeep-io-py is the python module that provides the interface to communicate with the backend or core components 
of real-time computer vision applications based on the [**DEEP-Framework**](https://github.com/crs4/deep_framework).
This module provides a class called [DeepIO](#DeepIO) which manages the streaming of video and data to and from the 
application core.
\n\n# Features\n\n
- Built on top of Python’s standard asynchronous I/O framework [**asyncio**](https://docs.python.org/3/library/asyncio.html?highlight=asyncio#module-asyncio), 
and [**hyperpeer-py**](https://github.com/crs4/hyperpeer-py) . \n
\n\n# API Reference\n\n
"

{ echo -e $intro & pydocmd simple deep_io.deep_io.DeepIO+; } > README.md