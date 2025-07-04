import socket
from concurrent.futures import ProcessPoolExecutor
from http import HttpServer
import logging

httpserver = HttpServer()

def ProcessTheClient(connection, address):
    try:
        buffer = b''
        while True:
            chunk = connection.recv(4096)
            if not chunk:
                break
            buffer += chunk
            if b'\r\n\r\n' in buffer:
                headers_part = buffer.split(b'\r\n\r\n')[0].decode()
                header_lines = headers_part.split('\r\n')
                content_length = 0
                for line in header_lines:
                    if line.lower().startswith('content-length:'):
                        content_length = int(line.split(':', 1)[1].strip())
                        break
                total_length_expected = len(headers_part.encode()) + 4 + content_length
                if len(buffer) >= total_length_expected:
                    break

        request = buffer.decode()
        response = httpserver.proses(request)
        connection.sendall(response)
    except Exception as e:
        print(f"Error processing client {address}: {e}")
    finally:
        connection.close()

def Server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('0.0.0.0', 8889))
        s.listen(5)
        print("Server running on port 8889 with ProcessPoolExecutor")
        with ProcessPoolExecutor(20) as executor:
            the_clients = []
            while True:
                conn, addr = s.accept()
                p = executor.submit(ProcessTheClient, conn, addr)
                the_clients.append(p)

                jumlah = ['x' for i in the_clients if i.running()]
                print(jumlah)

if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    Server()
