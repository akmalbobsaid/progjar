import socket
import json
import base64
import logging
import os

def send_command(command_str="", server_address=None):
    if not server_address:
        logging.error("Server address is not set.")
        return None

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        logging.warning(f"connecting to {server_address}")
        sock.connect(server_address)
        
        command_with_terminator = command_str + "\r\n\r\n"
        
        logging.warning(f"sending command: {command_str[:30]}...")
        sock.sendall(command_with_terminator.encode())
        
        data_received = ""
        while True:
            data = sock.recv(4096)
            if data:
                data_received += data.decode()
                if "\r\n\r\n" in data_received:
                    break
            else:
                break
        
        cleaned_response = data_received.strip()
        hasil = json.loads(cleaned_response)
        return hasil
    except Exception as e:
        logging.error(f"Error during communication: {e}")
        return None
    finally:
        sock.close()
        logging.warning("connection closed")

def remote_list(server_address):
    command_str = "LIST"
    hasil = send_command(command_str, server_address)
    if hasil and hasil.get('status') == 'OK':
        print("\n📄 Daftar file di server:")
        if not hasil.get('data'):
            print("- (tidak ada file)")
        for nmfile in hasil.get('data', []):
            print(f"- {nmfile}")
        return True
    else:
        error_msg = hasil.get('data', 'Unknown error') if hasil else "Gagal terhubung ke server."
        print(f"Gagal mendapatkan daftar file. Error: {error_msg}")
        return False

def remote_get(filename, server_address):
    command_str = f"GET {filename}"
    hasil = send_command(command_str, server_address)
    if hasil and hasil.get('status') == 'OK':
        namafile = hasil.get('data_namafile')
        isifile = base64.b64decode(hasil.get('data_file'))
        with open(namafile, 'wb+') as fp:
            fp.write(isifile)
        print(f"File '{namafile}' berhasil diunduh.")
        return True
    else:
        error_msg = hasil.get('data', 'Unknown error') if hasil else "Gagal terhubung ke server."
        print(f"Gagal mengunduh file. Error: {error_msg}")
        return False

def remote_upload(local_filepath, server_address):
    if not os.path.exists(local_filepath):
        print(f"Error: File lokal '{local_filepath}' tidak ditemukan.")
        return False

    try:
        with open(local_filepath, 'rb') as fp:
            file_content = fp.read()
        
        encoded_content = base64.b64encode(file_content).decode()
        remote_filename = os.path.basename(local_filepath)
        
        command_str = f"UPLOAD {remote_filename} {encoded_content}"
        hasil = send_command(command_str, server_address)
        
        if hasil and hasil.get('status') == 'OK':
            print(f"File '{hasil.get('data_namafile')}' berhasil diunggah.")
            return True
        else:
            error_msg = hasil.get('data', 'Unknown error') if hasil else "Gagal terhubung ke server."
            print(f"Gagal mengunggah file. Error: {error_msg}")
            return False
    except Exception as e:
        print(f"Terjadi error saat proses upload: {e}")
        return False

def remote_delete(filename, server_address):
    command_str = f"DELETE {filename}"
    hasil = send_command(command_str, server_address)
    if hasil and hasil.get('status') == 'OK':
        print(f"File '{hasil.get('data_namafile')}' berhasil dihapus di server.")
        return True
    else:
        error_msg = hasil.get('data', 'Unknown error') if hasil else "Gagal terhubung ke server."
        print(f"Gagal menghapus file. Error: {error_msg}")
        return False

if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - client - %(message)s')
    server_address = ('127.0.0.1', 6666)

    dummy_filename = "testing_file.txt"
    with open(dummy_filename, 'w') as f:
        f.write("Ini adalah file uji coba.")
    
    print("--- MEMULAI PENGUJIAN CLIENT-SERVER ---")

    remote_list(server_address)

    print(f"\n[UNGGAH] Mencoba mengunggah '{dummy_filename}'...")
    remote_upload(dummy_filename, server_address)
    
    remote_list(server_address)
    
    print(f"\n[UNDUH] Mencoba mengunduh '{dummy_filename}'...")
    remote_get(dummy_filename, server_address)

    print(f"\n[HAPUS] Mencoba menghapus '{dummy_filename}'...")
    remote_delete(dummy_filename, server_address)

    remote_list(server_address)

    if os.path.exists(dummy_filename):
        os.remove(dummy_filename)
    print("\n--- PENGUJIAN SELESAI ---")
