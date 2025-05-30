import json
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
                cleaned = string_datamasuk[7:]  # hapus "UPLOAD "
                if "||" not in cleaned:
                    return json.dumps(dict(status='ERROR', data='Format upload tidak valid'))
                filename, base64_data = cleaned.split("||", 1)
                filename = filename.strip()
                base64_data = base64_data.strip()
                return json.dumps(self.file.upload([filename, base64_data]))
            except Exception as e:
                return json.dumps(dict(status='ERROR', data=f'Gagal upload file: {str(e)}'))

        try:
            c = shlex.split(string_datamasuk)
            if not c:
                return json.dumps(dict(status='ERROR', data='Empty request'))

            command = c[0].strip().upper()
            params = c[1:]
            if hasattr(self.file, command.lower()):
                method = getattr(self.file, command.lower())
                return json.dumps(method(params))
            return json.dumps(dict(status='ERROR', data='request tidak dikenali'))
        except Exception as e:
            return json.dumps(dict(status='ERROR', data=f'Exception: {str(e)}'))
