import json
import logging
import shlex
from file_interface import FileInterface

class FileProtocol:
    def __init__(self):
        self.file = FileInterface()
    
    def proses_string(self, string_datamasuk=''):
        logging.warning(f"string received: {string_datamasuk[:70]}...")
        
        c = shlex.split(string_datamasuk.lower())
        try:
            c_request = c[0].strip()
            logging.warning(f"processing request: {c_request}")
            params = [x for x in c[1:]]
            
            cl = getattr(self.file, c_request)(params)
            return json.dumps(cl)
        except AttributeError:
            logging.error(f"Unknown request: {c[0]}")
            return json.dumps(dict(status='ERROR',data='request tidak dikenali'))
        except Exception as e:
            logging.error(f"Error while processing string: {e}")
            return json.dumps(dict(status='ERROR',data=str(e)))
