import os
import json
import base64
import logging
from glob import glob

class FileInterface:
    def __init__(self):
        if not os.path.exists('files'):
            os.makedirs('files')
        os.chdir('files/')

    def list(self, params=[]):
        try:
            logging.warning("LIST: getting file list")
            filelist = glob('*.*')
            return dict(status='OK', data=filelist)
        except Exception as e:
            logging.error(f"LIST Error: {e}")
            return dict(status='ERROR', data=str(e))

    def get(self, params=[]):
        try:
            filename = params[0]
            if (filename == ''):
                return dict(status='ERROR', data='GET error: filename must be provided')
            
            logging.warning(f"GET: reading file {filename}")
            with open(f"{filename}", 'rb') as fp:
                isifile = base64.b64encode(fp.read()).decode()
            return dict(status='OK', data_namafile=filename, data_file=isifile)
        except FileNotFoundError:
            logging.error(f"GET Error: file {filename} not found")
            return dict(status='ERROR', data=f'File {filename} not found')
        except Exception as e:
            logging.error(f"GET Error: {e}")
            return dict(status='ERROR', data=str(e))

    def upload(self, params=[]):
        try:
            if len(params) < 2:
                return dict(status='ERROR', data='UPLOAD error: filename and file content must be provided')

            filename = params[0]
            filedata_base64 = params[1]
            
            filedata = base64.b64decode(filedata_base64)
            
            logging.warning(f"UPLOAD: writing file {filename} ({len(filedata)} bytes)")
            with open(filename, 'wb+') as fp:
                fp.write(filedata)
            
            return dict(status='OK', data_namafile=filename)
        except IndexError:
            return dict(status='ERROR', data="UPLOAD command requires filename and file data.")
        except Exception as e:
            logging.error(f"UPLOAD Error: {e}")
            return dict(status='ERROR', data=str(e))

    def delete(self, params=[]):
        try:
            filename = params[0]
            if not filename:
                 return dict(status='ERROR', data="DELETE error: Filename not provided.")

            if os.path.exists(filename):
                logging.warning(f"DELETE: removing file {filename}")
                os.remove(filename)
                return dict(status='OK', data_namafile=filename)
            else:
                logging.error(f"DELETE error: file {filename} not found")
                return dict(status='ERROR', data=f"File '{filename}' not found.")
        except IndexError:
            return dict(status='ERROR', data="DELETE command requires a filename.")
        except Exception as e:
            logging.error(f"DELETE error: {e}")
            return dict(status='ERROR', data=str(e))
