import sys
import socket
import logging
import ssl
import os
import base64

USE_HTTPS = False
DEST_HOST = 'localhost'
DEST_PORT = 8889  # thread:8885, process:8889

def make_socket(destination_address='localhost', port=12000):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (destination_address, port)
        logging.warning(f"[+] Connecting to {server_address}")
        sock.connect(server_address)
        return sock
    except Exception as e:
        logging.warning(f"[!] Error: {str(e)}")

def make_secure_socket(destination_address='localhost', port=10000):
    try:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        context.load_verify_locations(os.path.join(os.getcwd(), 'domain.crt'))

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (destination_address, port)
        logging.warning(f"[+] Connecting to {server_address} with TLS")
        sock.connect(server_address)
        secure_socket = context.wrap_socket(sock, server_hostname=destination_address)
        logging.warning(secure_socket.getpeercert())
        return secure_socket
    except Exception as e:
        logging.warning(f"[!] Secure socket error: {str(e)}")

def send_command(command_str, is_secure=False):
    host = DEST_HOST
    port = DEST_PORT

    if is_secure:
        sock = make_secure_socket(host, port)
    else:
        sock = make_socket(host, port)

    try:
        logging.warning(f"[>] Sending request...")
        sock.sendall(command_str.encode())
        response = ""
        while True:
            data = sock.recv(4096)
            if data:
                response += data.decode()
                if "\r\n\r\n" in response:
                    break
            else:
                break
        return response
    except Exception as e:
        logging.warning(f"[!] Error receiving data: {str(e)}")
        return None
    finally:
        sock.close()

def get_file(path='/'):
    cmd = f"""GET {path} HTTP/1.1\r
Host: {DEST_HOST}\r
User-Agent: myclient/1.0\r
Accept: */*\r
\r
"""
    return send_command(cmd, is_secure=USE_HTTPS)

def list_files(directory='.'):
    cmd = f"""GET /list?dir={directory} HTTP/1.1\r
Host: {DEST_HOST}\r
User-Agent: myclient/1.0\r
Accept: */*\r
\r
"""
    return send_command(cmd, is_secure=USE_HTTPS)

def delete_file(filename):
    cmd = f"""GET /delete/{filename} HTTP/1.1\r
Host: {DEST_HOST}\r
User-Agent: myclient/1.0\r
Accept: */*\r
\r
"""
    return send_command(cmd, is_secure=USE_HTTPS)

def upload_file(filepath):
    if not os.path.exists(filepath):
        print(f"[!] File not found: {filepath}")
        return

    filename = os.path.basename(filepath)
    with open(filepath, 'rb') as f:
        content = f.read()
    encoded = base64.b64encode(content).decode()

    body = f"{filename}||{encoded}"
    cmd = f"""POST /upload HTTP/1.1\r
Host: {DEST_HOST}\r
User-Agent: myclient/1.0\r
Accept: */*\r
Content-Length: {len(body)}\r
\r
{body}"""
    return send_command(cmd, is_secure=USE_HTTPS)

if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING)

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--get', help='GET file from server (e.g. /index.html)')
    parser.add_argument('--list', help='List files in directory (default: .)', nargs='?', const='.')
    parser.add_argument('--upload', help='Upload file to server')
    parser.add_argument('--delete', help='Delete file from server')
    parser.add_argument('--https', help='Use HTTPS (if server supports)', action='store_true')
    parser.add_argument('--host', help='Server host (default: localhost)', default='localhost')
    parser.add_argument('--port', help='Port (default: DEST_PORT)', type=int, default=DEST_PORT)

    args = parser.parse_args()

    DEST_HOST = args.host
    DEST_PORT = args.port
    USE_HTTPS = args.https

    if args.get:
        result = get_file(args.get)
    elif args.list is not None:
        result = list_files(args.list)
    elif args.upload:
        result = upload_file(args.upload)
    elif args.delete:
        result = delete_file(args.delete)
    else:
        print("No action specified. Use --help for options.")
        sys.exit(1)

    print(result)
