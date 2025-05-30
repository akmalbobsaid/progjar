import argparse
import os
import time
import socket
import base64
import json
import logging
import csv
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

BUFFER_SIZE = 65536
SERVER_ADDRESS = ('172.16.16.101', 1231)

TEST_FILES = {
    '10MB': 'file_10MB.dat',
    '50MB': 'file_50MB.dat',
    '100MB': 'file_100MB.dat'
}

def send_command(command_str):
    try:
        with socket.create_connection(SERVER_ADDRESS) as sock:
            sock.sendall((command_str + "\r\n\r\n").encode())
            data_received = ""
            while True:
                data = sock.recv(BUFFER_SIZE)
                if not data:
                    break
                data_received += data.decode()
                if "\r\n\r\n" in data_received:
                    break
            try:
                return json.loads(data_received)
            except json.JSONDecodeError:
                logging.error(f"Gagal decode JSON: {data_received}")
                return {'status': 'ERROR', 'data': 'Gagal decode respon server'}
    except Exception as e:
        return {'status': 'ERROR', 'data': str(e)}

def remote_list():
    hasil = send_command("LIST")
    if hasil and hasil.get('status') == 'OK':
        print("Daftar file:")
        for item in hasil.get('data', []):
            print("-", item)
        return hasil.get('data', [])
    else:
        print("Gagal LIST:", hasil.get('data', 'Unknown error'))
        return []

def remote_get(filename):
    start_time = time.time()
    hasil = send_command(f"GET {filename}")
    elapsed_time = time.time() - start_time

    if hasil and hasil.get('status') == 'OK':
        try:
            namafile = hasil['data_namafile']
            isifile = base64.b64decode(hasil['data_file'])
            with open(namafile, 'wb+') as fp:
                fp.write(isifile)
            return {'status': 'OK', 'filename': namafile, 'bytes': len(isifile), 'time': elapsed_time, 'error': None}
        except Exception as e:
            return {'status': 'ERROR', 'filename': filename, 'bytes': 0, 'time': elapsed_time, 'error': str(e)}
    else:
        return {'status': 'ERROR', 'filename': filename, 'bytes': 0, 'time': elapsed_time, 'error': hasil.get('data', 'Unknown error')}

def remote_upload(filepath):
    start_time = time.time()
    try:
        with open(filepath, 'rb') as f:
            file_bytes = f.read()
            encoded = base64.b64encode(file_bytes).decode()

        filename = os.path.basename(filepath)
        command_str = f"UPLOAD {filename}||{encoded}\r\n\r\n"
        hasil = send_command(command_str)
        elapsed_time = time.time() - start_time

        if hasil and hasil.get('status') == 'OK':
            return {'status': 'OK', 'filename': filename, 'bytes': len(file_bytes), 'time': elapsed_time, 'error': None}
        else:
            return {'status': 'ERROR', 'filename': filename, 'bytes': 0, 'time': elapsed_time, 'error': hasil.get('data', 'Unknown error')}
    except Exception as e:
        elapsed_time = time.time() - start_time
        return {'status': 'ERROR', 'filename': filepath, 'bytes': 0, 'time': elapsed_time, 'error': str(e)}

def run_stress_test(operation, size, client_pool_size):
    filename = TEST_FILES[size]
    results = []
    func = remote_upload if operation == 'UPLOAD' else remote_get
    target = filename if operation == 'UPLOAD' else os.path.basename(filename)

    with ThreadPoolExecutor(max_workers=client_pool_size) as executor:
        futures = [executor.submit(func, target) for _ in range(client_pool_size)]
        for future in as_completed(futures):
            try:
                result = future.result()
                if not isinstance(result, dict):
                    result = {'status': 'ERROR', 'filename': target, 'bytes': 0, 'time': 0, 'error': 'Invalid format'}
            except Exception as e:
                result = {'status': 'ERROR', 'filename': target, 'bytes': 0, 'time': 0, 'error': str(e)}
            results.append(result)
    return results

def run_single_test(test_no, op, size, client_pools, server_pools):
    results = run_stress_test(op, size, client_pools)
    success = sum(1 for r in results if r.get('status') == 'OK')
    fail = len(results) - success
    total_bytes = sum(r.get('bytes', 0) for r in results)
    total_time = sum(r.get('time', 0) for r in results if r.get('time', 0) > 0)
    throughput = total_bytes / total_time if total_time > 0 else 0

    row = [
        test_no, op, size, client_pools, server_pools,
        round(total_time, 2), int(throughput),
        success, fail, success, fail
    ]
    print(f"Done test #{test_no} - {op} {size} C:{client_pools} S:{server_pools}")
    return row

def restart_server(server_pool_size):
    try:
        subprocess.run(["pkill", "-f", "server.py"], check=True)
        subprocess.Popen(["python3", "server.py", "--pool", str(server_pool_size)])
        print(f"Server restarted with pool {server_pool_size}")
        time.sleep(3)
    except FileNotFoundError:
        print("Tidak dapat menemukan perintah pkill. Pastikan terinstall.")
    except subprocess.CalledProcessError as e:
        print(f"Gagal menghentikan server: {e}")
    except Exception as e:
        print(f"Gagal restart server: {e}")

def load_existing_results():
    if os.path.exists('stress_test_results.csv'):
        with open('stress_test_results.csv', 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader, None)
            if header == ['Test No', 'Operation', 'Size', 'Client Pool', 'Server Pool', 'Total Time (s)', 'Throughput (B/s)', 'Success Client', 'Fail Client', 'Success Server', 'Fail Server']:
                existing_tests = set()
                for row in reader:
                    try:
                        op, size, client_pool, server_pool = row[1], row[2], int(row[3]), int(row[4])
                        existing_tests.add((op, size, client_pool, server_pool))
                    except IndexError:
                        pass
                return existing_tests
    return set()

def stress_main(args):
    operations = ['UPLOAD', 'DOWNLOAD']
    sizes = ['10MB', '50MB', '100MB']
    client_pool_sizes = [1, 5, 50]
    server_pool_sizes = [1, 5, 50]

    existing_results = load_existing_results()
    test_no = 1
    if os.path.exists('stress_test_results.csv'):
        with open('stress_test_results.csv', 'r') as f:
            # Cari baris terakhir yang bukan header
            last_line = None
            for line in f:
                if "Test No" not in line:
                    last_line = line.strip().split(',')
            if last_line:
                try:
                    test_no = int(last_line[0]) + 1
                except ValueError:
                    test_no = 1
            else:
                test_no = 1
    else:
        with open('stress_test_results.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                'Test No', 'Operation', 'Size', 'Client Pool',
                'Server Pool', 'Total Time (s)', 'Throughput (B/s)',
                'Success Client', 'Fail Client', 'Success Server', 'Fail Server'
            ])

    if args.operation and args.size and args.client_pool and args.server_pool:
        op = args.operation.upper()
        size = args.size.upper()
        client_pool = int(args.client_pool)
        server_pool = int(args.server_pool)

        if op in operations and size in TEST_FILES and client_pool > 0 and server_pool > 0:
            restart_server(server_pool)
            result = run_single_test(test_no, op, size, client_pool, server_pool)
            with open('stress_test_results.csv', 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(result)
                csvfile.flush()
        else:
            print("Parameter tidak valid. Periksa --help.")
        return

    for server_pool in server_pool_sizes:
        restart_server(server_pool)
        for client_pool in client_pool_sizes:
            for size in sizes:
                for op in operations:
                    if (op, size, client_pool, server_pool) not in existing_results:
                        result = run_single_test(test_no, op, size, client_pool, server_pool)
                        with open('stress_test_results.csv', 'a', newline='') as csvfile:
                            writer = csv.writer(csvfile)
                            writer.writerow(result)
                            csvfile.flush()
                        test_no += 1
                    else:
                        print(f"Skipping test: {op} {size} C:{client_pool} S:{server_pool} (already in CSV)")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Client file server")
    parser.add_argument('--manual', action='store_true', help="Aktifkan mode manual")
    parser.add_argument('--operation', type=str, help="Operasi spesifik (UPLOAD/DOWNLOAD)")
    parser.add_argument('--size', type=str, help="Ukuran file spesifik (10MB/50MB/100MB)")
    parser.add_argument('--client-pool', type=int, help="Jumlah client pool spesifik")
    parser.add_argument('--server-pool', type=int, help="Jumlah server pool spesifik")
    args = parser.parse_args()

    logging.basicConfig(level=logging.WARNING)

    if args.manual:
        print("== Mode Manual ==")
        print("Perintah tersedia:")
        print("- list")
        print("- get <filename>")
        print("- upload <filepath>")
        print("- exit")

        while True:
            try:
                cmd = input(">> ").strip()
                if cmd == "exit":
                    break
                elif cmd == "list":
                    remote_list()
                elif cmd.startswith("get "):
                    filename = cmd.split(" ", 1)[1]
                    remote_get(filename)
                elif cmd.startswith("upload "):
                    filepath = cmd.split(" ", 1)[1]
                    remote_upload(filepath)
                else:
                    print("Perintah tidak dikenali.")
            except KeyboardInterrupt:
                print("\nKeluar.")
                break
    else:
        stress_main(args)
