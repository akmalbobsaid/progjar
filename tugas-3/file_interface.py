import socket
import json
import base64
import logging
import os

server_address = ('172.16.16.101', 1231)

def send_command(command_str=""):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(server_address)
        command_str += "\r\n\r\n"
        sock.sendall(command_str.encode())

        data_received = ""
        while True:
            data = sock.recv(1024)
            if data:
                data_received += data.decode()
                if "\r\n\r\n" in data_received:
                    break
            else:
                break

        return json.loads(data_received.strip())
    except Exception as e:
        logging.warning(f"Error: {e}")
        return dict(status='ERROR', data=str(e))
    finally:
        sock.close()

def remote_list():
    hasil = send_command("LIST")
    if hasil['status'] == 'OK':
        print("Daftar file:")
        for f in hasil['data']:
            print(f"- {f}")
    else:
        print(f"Gagal: {hasil['data']}")

def remote_get(filename=""):
    hasil = send_command(f"GET {filename}")
    if hasil['status'] == 'OK':
        with open(hasil['data_namafile'], 'wb') as f:
            f.write(base64.b64decode(hasil['data_file']))
        print(f"File '{filename}' berhasil di-download.")
    else:
        print(f"Gagal: {hasil['data']}")

def remote_upload(filepath):
    try:
        with open(filepath, 'rb') as f:
            encoded = base64.b64encode(f.read()).decode()
        filename = os.path.basename(filepath)
        command_str = f"UPLOAD {filename}||{encoded}"
        hasil = send_command(command_str)
        print(hasil['data'])
    except Exception as e:
        print(f"Gagal upload: {str(e)}")

def remote_delete(filename=""):
    hasil = send_command(f"DELETE {filename}")
    print(hasil['data'])

if __name__ == '__main__':
    remote_list()
    remote_get('donalbebek.jpg')
    remote_upload('file_upload.jpg')
    os.remove('file_upload.jpg')
    print("File file_upload.jpg pada local dihapus")
    remote_list()
    remote_get('file_upload.jpg')
    remote_delete('file_upload.jpg')
    remote_list()
