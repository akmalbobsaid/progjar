import os
import base64
from glob import glob

class FileInterface:
    def __init__(self):
        self.base_dir = 'files'
        os.makedirs(self.base_dir, exist_ok=True)

    def list(self, params=[]):
        try:
            filelist = glob(os.path.join(self.base_dir, '*.*'))
            filelist = [os.path.basename(f) for f in filelist]
            return dict(status='OK', data=filelist)
        except Exception as e:
            return dict(status='ERROR', data=str(e))

    def get(self, params=[]):
        try:
            filename = params[0]
            if not filename:
                return dict(status='ERROR', data='Filename kosong')
            filepath = os.path.join(self.base_dir, filename)
            with open(filepath, 'rb') as fp:
                content = base64.b64encode(fp.read()).decode()
            return dict(status='OK', data_namafile=filename, data_file=content)
        except Exception as e:
            return dict(status='ERROR', data=str(e))

    def upload(self, params=[]):
        try:
            filename = params[0]
            content_base64 = params[1].strip()
            filepath = os.path.join(self.base_dir, filename)
            content = base64.b64decode(content_base64)
            with open(filepath, 'wb') as fp:
                fp.write(content)
            return dict(status='OK', data=f'File {filename} berhasil diupload')
        except Exception as e:
            return dict(status='ERROR', data=str(e))

    def delete(self, params=[]):
        try:
            filename = params[0]
            filepath = os.path.join(self.base_dir, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                return dict(status='OK', data=f'File {filename} berhasil dihapus')
            return dict(status='ERROR', data='File tidak ditemukan')
        except Exception as e:
            return dict(status='ERROR', data=str(e))
