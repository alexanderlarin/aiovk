import os
import socket
import ssl
from http.server import BaseHTTPRequestHandler
from string import Template
from unittest.mock import patch
from urllib.parse import parse_qs

from jinja2 import Environment, FileSystemLoader
from yarl import URL

from aiovk import TokenSession, ImplicitSession
from tests.utils import TEST_DIR


def disable_cert_verification(func):
    @patch('ssl.create_default_context', ssl._create_unverified_context)
    def new_func(*inner_args, **inner_kwargs):
        func(*inner_args, **inner_kwargs)
    return new_func


class HtmlTemplate(Template):
    pattern = r"""
        %(delim)s(?:
          (?P<escaped>%(delim)s) |   # Escape sequence of two delimiters
          {{ (?P<braced>%(id)s) }} |   # delimiter and a braced identifier
          (?P<invalid>)              # Other ill-formed delimiter exprs
        )
        """


class VKRequestHandler(BaseHTTPRequestHandler):
    base_file_dir = os.path.join(TEST_DIR, 'responses')
    templates = Environment(loader=FileSystemLoader(base_file_dir))
    token = 'token'

    def redirect(self, url):
        self.send_response(301)
        self.send_header('Location', url)
        self.end_headers()

    def html_pages(self, filename, mime_type=None, context=None):
        if mime_type is None:
            mime_type = 'text/html'
        if context is None:
            context = {}
        self.send_response(200)
        self.send_header('Content-type', mime_type)
        self.end_headers()
        template = self.templates.get_template(filename)
        self.wfile.write(template.render(**context).encode())

    def json_response(self, filename, context=None):
        self.html_pages(filename, 'application/json', context=context)

    def do_GET(self):
        url = URL(self.path)
        if url.path == '/authorize' and 'client_id' in url.query:
            self.html_pages('authorize_page.html', context={'base_url': self.headers['Host']})
            return
        elif url.path == '/blank.html':
            self.html_pages('blank.html')
            return
        elif url.path == '/method/messages.getLongPollServer':
            if url.query.get('access_token') == self.token:
                self.json_response('getLongPollServer.success.json', context={'base_url': self.headers['Host']})
                return
            else:
                self.json_response('getLongPollServer.error.json')
                return
        elif url.path == '/im1774':
            self.json_response('LongPoolWait.json')
            return
        elif url.path == '/method/users.get':
            self.json_response('users.get.json')
            return
        elif url.path == '/method/users.get.error':
            self.json_response('users.get.error.json')
            return
        else:
            pass

    def do_POST(self):
        url = URL(self.path)
        if url.query.get('act', None) == 'login':
            content_length = int(self.headers['Content-Length'])  # <--- Gets the size of data
            post_data = self.rfile.read(content_length)  # <--- Gets the data itself
            post_data = parse_qs(post_data.decode())
            if 'email' in post_data:
                redirect_url = 'https://{}/blank.html#access_token={}'.format(self.headers['Host'], self.token)
                self.redirect(redirect_url)
            else:
                self.html_pages('blank.html')
            return
        else:
            pass


class BaseUnittestSession:
    BASE_URL = '127.0.0.1:8000'

    @property
    def AUTH_URL(self):
        return 'https://' + self.BASE_URL + '/authorize'

    @property
    def REQUEST_URL(self):
        return 'https://' + self.BASE_URL + '/method/'


class TestTokenSession(BaseUnittestSession, TokenSession):
    pass


class TestInternalAuthSession(BaseUnittestSession, ImplicitSession):
    pass


def get_free_port():
    s = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM)
    s.bind(('localhost', 0))
    address, port = s.getsockname()
    s.close()
    return port


class MockServerRequestHandler(BaseHTTPRequestHandler):
    json_filepath = os.path.join(TEST_DIR, 'responses', "testdata.json")

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