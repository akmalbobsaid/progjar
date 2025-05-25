import socket
import json
import base64
import logging
import os

server_address = ('0.0.0.0', 7777)

def send_command(command_str=""):
    global server_address
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(server_address)
    logging.warning(f"connecting to {server_address}")
    try:
        command_str += "\r\n\r\n"
        sock.sendall(command_str.encode())

        data_received = ""
        while True:
            data = sock.recv(1024)
            if not data:
                break
            data_received += data.decode()
            if "\r\n\r\n" in data_received:
                break

        hasil = json.loads(data_received.strip("\r\n\r\n"))
        logging.warning("data received from server:")
        return hasil
    except Exception as e:
        logging.warning(f"error during data receiving: {e}")
        return False
    finally:
        sock.close()

def remote_list():
    command_str = "LIST"
    hasil = send_command(command_str)
    if hasil and hasil['status'] == 'OK':
        print("Daftar file:")
        for nmfile in hasil['data']:
            print(f"- {nmfile}")
        return True
    else:
        print("Gagal mendapatkan daftar file")
        return False

def remote_get(filename=""):
    command_str = f"GET {filename}"
    hasil = send_command(command_str)
    if hasil and hasil['status'] == 'OK':
        namafile = hasil['data_namafile']
        isifile = base64.b64decode(hasil['data_file'])
        with open(namafile, 'wb') as fp:
            fp.write(isifile)
        print(f"File '{namafile}' berhasil di-download.")
        return True
    else:
        print("Gagal mendapatkan file:", hasil.get("data", "Unknown error"))
        return False

def remote_upload(filepath):
    try:
        with open(filepath, 'rb') as f:
            encoded = base64.b64encode(f.read()).decode()

        filename = os.path.basename(filepath)
        command_str = f"UPLOAD {filename}||{encoded}"
        hasil = send_command(command_str)
        if hasil['status'] == 'OK':
            print(f"Berhasil upload file: {filename}")
            return True
        else:
            print(f"Gagal upload file: {hasil['data']}")
            return False
    except Exception as e:
        print(f"Gagal upload file: {str(e)}")
        return False

def remote_delete(remote_filename=""):
    command_str = f"DELETE {remote_filename}"
    hasil = send_command(command_str)
    if hasil and hasil['status'] == 'OK':
        print(f"File '{remote_filename}' berhasil dihapus dari server.")
        return True
    else:
        print("Gagal menghapus file:", hasil.get('data', 'Unknown error'))
        return False

if __name__ == '__main__':
    server_address = ('172.16.16.101', 1231)

    remote_list()
    remote_get('donalbebek.jpg')
    remote_upload('test_upload.jpg')
    os.remove('test_upload.jpg')
    print("File test_upload.jpg pada local dihapus")
    print(os.listdir("."))
    remote_list()
    remote_get('test_upload.jpg')
    remote_delete('test_upload.jpg')
    remote_list()
