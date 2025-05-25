import socket
import json
import base64
import logging
import os

server_address = ('0.0.0.0', 7777)


def send_command(command_str=""):
    global server_address
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(server_address)
        logging.warning(f"connecting to {server_address}")
        command_str += "\r\n\r\n"
        logging.warning(f"sending message: {command_str.strip()}")
        sock.sendall(command_str.encode())
        data_received = ""
        while True:
            data = sock.recv(16)
            if data:
                data_received += data.decode()
                if "\r\n\r\n" in data_received:
                    break
            else:
                break
        try:
            hasil = json.loads(data_received.strip())
            logging.warning(f"data received from server: {hasil}")
            return hasil
        except json.JSONDecodeError:
            logging.warning(f"Error decoding JSON: {data_received}")
            return {'status': 'ERROR', 'data': 'Invalid JSON response'}
    except ConnectionRefusedError:
        logging.warning(f"Connection to {server_address} refused.")
        return False
    except Exception as e:
        logging.warning(f"error during data receiving: {e}")
        return False
    finally:
        sock.close()


def remote_list():
    command_str = "LIST"
    hasil = send_command(command_str)
    if hasil and hasil.get('status') == 'OK':
        print("daftar file : ")
        for nmfile in hasil['data']:
            print(f"- {nmfile}")
        return True
    else:
        print("Gagal mendapatkan daftar file:", hasil.get('data', 'Unknown error'))
        return False


def remote_get(filename=""):
    command_str = f"GET {filename}"
    hasil = send_command(command_str)
    if hasil and hasil.get('status') == 'OK':
        namafile = hasil['data_namafile']
        isifile = base64.b64decode(hasil['data_file'])
        with open(namafile, 'wb+') as fp:
            fp.write(isifile)
        print(f"File '{namafile}' berhasil di-download.")
        return True
    else:
        print(f"Gagal mendapatkan file '{filename}':", hasil.get('data', 'Unknown error'))
        return False


def remote_upload(filepath):
    try:
        with open(filepath, 'rb') as f:
            encoded = base64.b64encode(f.read()).decode()

        filename = os.path.basename(filepath)
        command_str = f"UPLOAD {filename}||{encoded}"
        hasil = send_command(command_str)
        if hasil and hasil.get('status') == 'OK':
            print(f"Berhasil upload file '{filename}': {hasil['data']}")
            return True
        else:
            print(f"Gagal upload file '{filename}': {hasil.get('data', 'Unknown error')}")
            return False
    except FileNotFoundError:
        print(f"Error: File '{filepath}' tidak ditemukan.")
        return False
    except Exception as e:
        print(f"Gagal upload file: {str(e)}")
        return False

def remote_delete(remote_filename=""):
    command_str = f"DELETE {remote_filename}"
    hasil = send_command(command_str)
    if hasil and hasil.get('status') == 'OK':
        print(f"File '{remote_filename}' berhasil dihapus dari server: {hasil['data']}")
        return True
    else:
        print(f"Gagal menghapus file '{remote_filename}':", hasil.get('data', 'Unknown error'))
        return False


if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING)
    server_address = ('127.0.0.1', 1231)  # Using localhost for testing

    print("\n--- File Client ---")
    while True:
        command = input("Masukkan perintah (LIST, GET <namafile>, UPLOAD <filepath>, DELETE <namafile>, EXIT): ").strip().upper().split()
        if not command:
            continue
        if command[0] == 'LIST':
            remote_list()
        elif command[0] == 'GET':
            if len(command) > 1:
                remote_get(command[1])
            else:
                print("Penggunaan: GET <namafile>")
        elif command[0] == 'UPLOAD':
            if len(command) > 1:
                remote_upload(command[1])
            else:
                print("Penggunaan: UPLOAD <filepath>")
        elif command[0] == 'DELETE':
            if len(command) > 1:
                remote_delete(command[1])
            else:
                print("Penggunaan: DELETE <namafile>")
        elif command[0] == 'EXIT':
            break
        else:
            print("Perintah tidak dikenali.")
