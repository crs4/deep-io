import os
from deep_io.deep_io import DeepIO
import logging 
from pathlib import Path
import urllib.request

source_id = os.environ["STREAM_CAPTURE_ID"].rstrip()
logging.info('STREAM_CAPTURE_ID: ' + source_id)
source_url = os.environ[f'SOURCE_{source_id}'].rstrip()
logging.info('Source URL: ' + source_url)
#source_format = os.environ.get("SOURCE_FORMAT", 'mpjpeg')
source_metadata = os.environ.get("STREAM_METADATA", {'url': source_url})
remote_peer_type = os.environ.get("REMOTE_PEER_TYPE", None)
server_address = os.environ['HP_SERVER']
server_port = os.environ['SERVER_PORT']

try:
    req = urllib.request.Request(source_url)
    urllib.request.urlopen(req)
except (ValueError, urllib.error.URLError) as e:
    logging.info(f'source is not a standard url...')
    if not source_url.startswith('rtsp:'):
        logging.info(f'source is neither a rtsp url ...')
        if not Path(source_url).is_file():
            logging.error(f'source is neither a file ...')
            # raise Exception(f'Invalid source ({source_url}): {str(e)}')
    
    #sys.exit()

if source_url.endswith('mjpg'):
    source_format = 'mpjpeg'
elif source_url.startswith('/dev'):
    source_format = 'v4l2'
else:
    source_format = None

import json
output_file_path = os.environ.get('OUTPUT_FILE', "messages.txt")

with  open(output_file_path, 'w') as output_file:
    def print_to_file(data):
        if data['type'] == 'data':
            data_to_save = {
                'vc_time': data['vc_time'],
                'last_frame_shape': data['last_frame_shape'],
                'data': data['data']
            }
            output_json = json.dumps(data_to_save)
            output_file.write(output_json + '\n')
    stream_capture = DeepIO(server_address, server_port, source_url, peer_id=source_id, peer_type='stream_capture', format=source_format, metadata=source_metadata, remotePeerType=remote_peer_type)
    # stream_capture.add_data_handler(lambda data: logging.info(f'*** Remote message: {str(data)}'))
    stream_capture.add_data_handler(print_to_file)
    stream_capture.run()