#!/usr/bin/env python

import os
import stat
import subprocess
import http.server
import socketserver
import threading

FILE_PATH = os.environ.get('FILE_PATH', './.tmp')
PORT = int(os.environ.get('SERVER_PORT') or os.environ.get('PORT') or 1110)
openhttp = os.getenv('OPENHTTP', '1')

start_script_path = os.path.abspath('./start.sh')
start_script_dir = os.path.dirname(start_script_path)
os.chmod(start_script_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)

env = os.environ.copy()
env['OPENHTTP'] = openhttp
try:
    start_script = subprocess.Popen(
        [start_script_path],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        cwd=start_script_dir  # 设置 start.sh 的工作目录
    )
    # print(f"Started start.sh (PID: {start_script.pid})")

    def log_stream(stream):
        for line in stream:
            print(line, end='', flush=True)

    threading.Thread(target=log_stream, args=(start_script.stdout,), daemon=True).start()
    threading.Thread(target=log_stream, args=(start_script.stderr,), daemon=True).start()
except Exception as e:
    print("Error starting start.sh:", str(e))

if openhttp == '1':
    class MyHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/':
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'Hello, world')
            elif self.path == '/sub':
                try:
                    with open(os.path.join(FILE_PATH, 'log.txt'), 'rb') as file:
                        content = file.read()
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/plain; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(content)
                except FileNotFoundError:
                    self.send_response(500)
                    self.end_headers()
                    self.wfile.write(b'Error reading file')
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'Not found')

    httpd = socketserver.TCPServer(('', PORT), MyHandler)
    server_thread = threading.Thread(target=httpd.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    print('server is listening on port :', PORT)
    server_thread.join()
elif openhttp == '0':
    print('server is listening on port :', PORT)
    start_script.wait()
