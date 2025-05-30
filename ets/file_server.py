import socket
import argparse
import logging
import json
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from file_protocol import FileProtocol

HOST = '0.0.0.0'
PORT = 1231
BUFFER_SIZE = 65536
DELIMITER = "\r\n\r\n"

fp = FileProtocol()

def read_full_request(conn):
    data_received = ""
    while True:
        data = conn.recv(BUFFER_SIZE)
        if not data:
            break
        data_received += data.decode()
        if DELIMITER in data_received:
            break
    return data_received.strip()

def handle_client_thread(conn, addr):
    logging.warning(f"[THREAD] Connection from {addr}")
    try:
        request = read_full_request(conn)
        response = fp.proses_string(request) + DELIMITER
        conn.sendall(response.encode())
    except Exception as e:
        logging.warning(f"[THREAD] Error: {e}")
    finally:
        conn.close()
        logging.warning(f"[THREAD] Connection from {addr} closed")

def handle_client_process(request_string):
    try:
        fp_local = FileProtocol()
        response = fp_local.proses_string(request_string)
        return response
    except Exception as e:
        return json.dumps(dict(status="ERROR", data=f"Process error: {str(e)}"))

def main(pool_size, mode):
    logging.basicConfig(level=logging.WARNING)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(100)
    logging.warning(f"Server running on {HOST}:{PORT} using {mode.upper()} pool")

    if mode == "process":
        with ProcessPoolExecutor(max_workers=pool_size) as executor:
            while True:
                conn, addr = server_socket.accept()
                request = read_full_request(conn)
                future = executor.submit(handle_client_process, request)
                response = future.result() + DELIMITER
                try:
                    conn.sendall(response.encode())
                except:
                    pass
                conn.close()
                logging.warning(f"[PROCESS] Connection from {addr} closed")
    else:
        with ThreadPoolExecutor(max_workers=pool_size) as executor:
            while True:
                conn, addr = server_socket.accept()
                executor.submit(handle_client_thread, conn, addr)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pool-based File Server")
    parser.add_argument('--pool', type=int, default=5,
                        help="Jumlah maksimal worker pool")
    parser.add_argument('--mode', type=str, default='thread', choices=['thread', 'process'],
                        help="Mode concurrency: 'thread' atau 'process'")
    args = parser.parse_args()
    main(args.pool, args.mode)
