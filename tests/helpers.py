import os
import socket
import webbrowser
from http.server import BaseHTTPRequestHandler

import pyotp

from aiovk import ImplicitSession
from tests.auth_data import TWOFACTOR_CODE


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


class TestAuthSession(ImplicitSession):
    async def enter_confirmation_сode(self):
        totp = pyotp.TOTP(TWOFACTOR_CODE)
        return totp.now()

    async def enter_captcha(self, url, sid):
        bytes = await self.driver.get_bin(url, {})
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "captcha.jpg")
        with open(file_path, 'wb') as f:
            f.write(bytes)
        webbrowser.open("file://{}".format(file_path))
        code = input("Enter captcha: ")
        os.remove(file_path)
        return code
