import os
import json
import base64
from glob import glob

class FileInterface:
    def __init__(self):
        self.base_dir = 'files'
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)

    def list(self, params=[]):
        try:
            filelist = glob(os.path.join(self.base_dir, '*.*'))
            filelist = [os.path.basename(f) for f in filelist]
            return dict(status='OK', data=filelist)
        except Exception as e:
            return dict(status='ERROR', data=str(e))

    def get(self, params=[]):
        try:
            if not params:
                return dict(status='ERROR', data='Parameter nama file dibutuhkan')
            filename = params[0]
            filepath = os.path.join(self.base_dir, filename)
            if not os.path.exists(filepath):
                return dict(status='ERROR', data='File tidak ditemukan')
            with open(filepath, 'rb') as fp:
                isifile = base64.b64encode(fp.read()).decode()
            return dict(status='OK', data_namafile=filename, data_file=isifile)
        except Exception as e:
            return dict(status='ERROR', data=str(e))

    def upload(self, params=[]):
        try:
            if len(params) < 2:
                return dict(status='ERROR', data='Parameter upload tidak lengkap')
            filename = params[0]
            b64content = params[1].strip()
            content = base64.b64decode(b64content)
            filepath = os.path.join(self.base_dir, filename)
            with open(filepath, 'wb') as fp:
                fp.write(content)
            return dict(status='OK', data=f'File {filename} berhasil diupload')
        except Exception as e:
            return dict(status='ERROR', data=str(e))

    def delete(self, params=[]):
        try:
            if not params:
                return dict(status='ERROR', data='Parameter nama file dibutuhkan')
            filename = params[0]
            filepath = os.path.join(self.base_dir, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                return dict(status='OK', data=f'File {filename} berhasil dihapus')
            else:
                return dict(status='ERROR', data='File tidak ditemukan')
        except Exception as e:
            return dict(status='ERROR', data=str(e))
