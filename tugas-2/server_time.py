import socket
import threading
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class ProcessTheClient(threading.Thread):
    def __init__(self, connection, address):
        self.connection = connection
        self.address = address
        threading.Thread.__init__(self)

    def run(self):
        while True:
            try:
                data = self.connection.recv(1024)
                if not data:
                    break

                request = data.decode('utf-8').strip()

                if request == "TIME":
                    now = datetime.now()
                    time_str = now.strftime("%H:%M:%S")
                    
                    response = f"JAM {time_str}\r\n"
                    
                    self.connection.sendall(response.encode('utf-8'))
                
                elif request == "QUIT":
                    break
                
                else:
                    error_msg = "Perintah tidak dikenali. Gunakan TIME atau QUIT.\r\n"
                    self.connection.sendall(error_msg.encode('utf-8'))

            except socket.error as e:
                logging.error(f"Socket error with {self.address}: {e}")
                break

        logging.info(f"Connection from {self.address} closed.")
        self.connection.close()

class Server(threading.Thread):
    def __init__(self, port):
        self.port = port
        self.the_clients = []
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        threading.Thread.__init__(self)

    def run(self):
        self.my_socket.bind(('0.0.0.0', self.port))
        self.my_socket.listen(5)
        logging.info(f"Time server listening on port {self.port}...")

        while True:
            connection, client_address = self.my_socket.accept()
            logging.info(f"Accepted connection from {client_address}")
            
            client_thread = ProcessTheClient(connection, client_address)
            client_thread.start()
            
            self.the_clients.append(client_thread)
	
def main():
    server = Server(45000)
    server.start()

if __name__ == "__main__":
    main()
