import os
import uuid
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import base64

class HttpServer:
    def __init__(self):
        self.sessions = {}
        self.types = {
            '.pdf': 'application/pdf',
            '.jpg': 'image/jpeg',
            '.txt': 'text/plain',
            '.html': 'text/html'
        }

    def response(self, kode=404, message='Not Found', messagebody=bytes(), headers={}):
        tanggal = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        resp = [
            f"HTTP/1.1 {kode} {message}\r\n",
            f"Date: {tanggal}\r\n",
            "Connection: close\r\n",
            "Server: myserver/1.0\r\n",
            f"Content-Length: {len(messagebody)}\r\n"
        ]

        for kk, vv in headers.items():
            resp.append(f"{kk}: {vv}\r\n")
        resp.append("\r\n")

        if type(messagebody) is not bytes:
            messagebody = messagebody.encode()

        response_headers = "".join(resp).encode()
        return response_headers + messagebody

    def proses(self, data):
        try:
            headers_body = data.split('\r\n\r\n', 1)
            header_lines = headers_body[0].split('\r\n')
            body = headers_body[1] if len(headers_body) > 1 else ''
    
            request_line = header_lines[0]
            parts = request_line.split()
            if len(parts) != 3:
                return self.response(400, 'Bad Request', 'Malformed request line.')
    
            method, path, version = parts
            method = method.upper()
    
            headers = {}
            for line in header_lines[1:]:
                if ':' in line:
                    k, v = line.split(':', 1)
                    headers[k.strip().lower()] = v.strip()
    
            if version == 'HTTP/1.1' and 'host' not in headers:
                return self.response(400, 'Bad Request', 'Missing Host header.')
    
            if method == 'POST':
                content_length = int(headers.get('content-length', '0'))
                if len(body.encode()) < content_length:
                    return self.response(400, 'Bad Request', 'Incomplete POST body.')
                return self.http_post(path, headers, body)
    
            elif method == 'GET':
                return self.http_get(path, headers)
    
            else:
                return self.response(501, 'Not Implemented', f'Method {method} not supported.')
        except Exception as e:
            return self.response(500, 'Internal Server Error', str(e))

    def http_get(self, path, headers):
        parsed = urlparse(path)
        route = parsed.path
        query = parse_qs(parsed.query)

        if route == '/list':
            target_dir = query.get('dir', ['./'])[0]
            if not os.path.isdir(target_dir):
                return self.response(404, 'Not Found', 'Directory not found.')

            files = os.listdir(target_dir)
            body = "\n".join(files)
            return self.response(200, 'OK', body, {'Content-Type': 'text/plain'})

        if route.startswith('/delete/'):
            filename = route[len('/delete/'):]
            safe_path = os.path.abspath(filename)
            if not safe_path.startswith(os.getcwd()):
                return self.response(403, 'Forbidden', 'Access denied.')

            if os.path.isfile(safe_path):
                os.remove(safe_path)
                return self.response(200, 'OK', f'{filename} deleted.', {'Content-Type': 'text/plain'})
            else:
                return self.response(404, 'Not Found', 'File not found.')

        if route == '/':
            return self.response(200, 'OK', 'Welcome to the experimental web server.', {'Content-Type': 'text/plain'})
        elif route == '/video':
            return self.response(302, 'Found', '', {'Location': 'https://youtu.be/katoxpnTf04'})
        elif route == '/santai':
            return self.response(200, 'OK', 'santai saja', {'Content-Type': 'text/plain'})

        filepath = route.lstrip('/')
        if not os.path.isfile(filepath):
            return self.response(404, 'Not Found', f'{filepath} not found.')

        with open(filepath, 'rb') as f:
            content = f.read()

        ext = os.path.splitext(filepath)[1]
        content_type = self.types.get(ext, 'application/octet-stream')
        return self.response(200, 'OK', content, {'Content-Type': content_type})

    def http_post(self, path, headers, body):
        if path == '/upload':
            try:
                if '||' not in body:
                    return self.response(400, 'Bad Request', 'Invalid format. Expecting filename||data.')

                filename, encoded = body.strip().split('||', 1)
                binary_data = base64.b64decode(encoded)

                with open(filename, 'wb') as f:
                    f.write(binary_data)

                return self.response(200, 'OK', f'File {filename} uploaded.', {'Content-Type': 'text/plain'})
            except Exception as e:
                return self.response(500, 'Internal Server Error', str(e))

        return self.response(400, 'Bad Request', 'Unknown POST path.')
