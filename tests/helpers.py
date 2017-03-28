import os
import socket
from http.server import BaseHTTPRequestHandler


def get_free_port():
    s = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM)
    s.bind(('localhost', 0))
    address, port = s.getsockname()
    s.close()
    return port


class MockServerRequestHandler(BaseHTTPRequestHandler):
    json_filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "testdata.json")

    def log_message(self, format, *args):
        # Disable logging
        return

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        with open(self.json_filepath) as f:
            self.wfile.write(f.read().encode())

    def do_POST(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write("OK".encode())
