import socket
import threading
import logging
from file_protocol import FileProtocol

fp = FileProtocol()

class ProcessTheClient(threading.Thread):
    def __init__(self, connection, address):
        super().__init__()
        self.connection = connection
        self.address = address

    def run(self):
        try:
            buffer = ""
            while True:
                data = self.connection.recv(1024)
                if data:
                    buffer += data.decode()
                    if "\r\n\r\n" in buffer:
                        break
                else:
                    break

            if buffer:
                request = buffer.strip("\r\n\r\n")
                response = fp.proses_string(request)
                self.connection.sendall((response + "\r\n\r\n").encode())
        except Exception as e:
            logging.warning(f"Error handling client {self.address}: {str(e)}")
        finally:
            self.connection.close()

class Server(threading.Thread):
    def __init__(self, ipaddress='0.0.0.0', port=1231):
        super().__init__()
        self.ipinfo = (ipaddress, port)
        self.the_clients = []
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def run(self):
        logging.warning(f"Server berjalan di {self.ipinfo}")
        self.my_socket.bind(self.ipinfo)
        self.my_socket.listen(5)
        while True:
            conn, addr = self.my_socket.accept()
            logging.warning(f"Koneksi dari {addr}")
            clt = ProcessTheClient(conn, addr)
            clt.start()
            self.the_clients.append(clt)

if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    Server().start()
