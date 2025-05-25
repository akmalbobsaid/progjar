import json
import logging
import shlex
import base64
from file_interface import FileInterface

class FileProtocol:
    def __init__(self):
        self.file = FileInterface()

    def proses_string(self, string_datamasuk=''):
        string_datamasuk = string_datamasuk.strip()
        if string_datamasuk.upper().startswith("UPLOAD "):
            try:
                cleaned = string_datamasuk[7:]
                if "||" not in cleaned:
                    return json.dumps(dict(status='ERROR', data='Format upload tidak valid'))

                filename, base64_data = cleaned.split("||", 1)
                return json.dumps(self.file.upload([filename.strip(), base64_data.strip()]))
            except Exception as e:
                return json.dumps(dict(status='ERROR', data=f'Gagal upload file: {str(e)}'))

        # proses LIST, GET, DELETE
        try:
            c = shlex.split(string_datamasuk)
            c_request = c[0].strip().upper()
            params = c[1:]

            if hasattr(self.file, c_request.lower()):
                cl = getattr(self.file, c_request.lower())(params)
                return json.dumps(cl)
            else:
                return json.dumps(dict(status='ERROR', data='request tidak dikenali'))
        except Exception as e:
            return json.dumps(dict(status='ERROR', data=f'Exception: {str(e)}'))
