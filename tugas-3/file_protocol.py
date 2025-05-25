import json
import logging
import shlex
import base64

from file_interface import FileInterface

"""
* class FileProtocol bertugas untuk memproses
data yang masuk, dan menerjemahkannya apakah sesuai dengan
protokol/aturan yang dibuat

* data yang masuk dari client adalah dalam bentuk bytes yang
pada akhirnya akan diproses dalam bentuk string

* class FileProtocol akan memproses data yang masuk dalam bentuk
string
"""


class FileProtocol:
    def __init__(self):
        self.file = FileInterface()

    def proses_string(self, string_datamasuk=''):
        string_datamasuk = string_datamasuk.strip()
        logging.warning(f"string diproses: '{string_datamasuk}'")
        try:
            c = shlex.split(string_datamasuk)
            if not c:
                return json.dumps({'status': 'ERROR', 'data': 'Empty request'}) + "\r\n\r\n"

            c_request = c[0].strip().upper()
            params = c[1:]
            logging.warning(f"memproses request: {c_request}, dengan parameter: {params}")

            if hasattr(self.file, c_request.lower()):
                cl = getattr(self.file, c_request.lower())(params)
                return json.dumps(cl) + "\r\n\r\n"
            else:
                return json.dumps({'status': 'ERROR', 'data': f'Request "{c_request}" tidak dikenali'}) + "\r\n\r\n"
        except Exception as e:
            logging.error(f"Error processing request '{string_datamasuk}': {e}")
            return json.dumps({'status': 'ERROR', 'data': str(e)}) + "\r\n\r\n"


if __name__ == '__main__':
    # contoh pemakaian
    fp = FileProtocol()
    print(fp.proses_string("LIST"))
    print(fp.proses_string("GET pokijan.jpg"))
    encoded = base64.b64encode(b'This is a test upload via protocol.').decode()
    upload_command = f"UPLOAD test_protocol_upload.txt||{encoded}"
    print(fp.proses_string(upload_command))
    print(fp.proses_string("DELETE test_protocol_upload.txt"))
