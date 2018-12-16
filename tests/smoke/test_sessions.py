import os
import ssl
import unittest
from http.server import HTTPServer
from threading import Thread

from aiohttp.test_utils import unittest_run_loop

from aiovk import ImplicitSession, TokenSession
from aiovk.exceptions import VkAuthError
from tests.smoke.utils import disable_cert_verification, VKRequestHandler, get_free_port
from tests.utils import AioTestCase, TEST_DIR


class TokenSessionTestCase(AioTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Configure mock server.
        cls.mock_server_port = get_free_port()
        cls.mock_server = HTTPServer(('localhost', cls.mock_server_port), VKRequestHandler)
        cls.mock_server.socket = ssl.wrap_socket(cls.mock_server.socket, server_side=True,
                                                 certfile=os.path.join(TEST_DIR, 'certs', 'cert.pem'),
                                                 keyfile=os.path.join(TEST_DIR, 'certs', 'key.pem'))

        # Start running mock server in a separate thread.
        # Daemon threads automatically shut down when the main process exits.
        cls.mock_server_thread = Thread(target=cls.mock_server.serve_forever)
        cls.mock_server_thread.setDaemon(True)
        cls.mock_server_thread.start()
        cls.base_url = 'localhost:{port}'.format(port=cls.mock_server_port)

        cls.json_url = 'https://{}/'.format(cls.base_url)

    @unittest_run_loop
    async def test_auth_with_empty_token(self):
        s = TokenSession()
        with self.assertRaises(VkAuthError):
            await s.authorize()
        await s.close()

    @disable_cert_verification
    @unittest_run_loop
    async def test_auth_with_token(self):
        s = TokenSession('token')
        with self.assertRaises(VkAuthError):
            await s.authorize()
        await s.close()

    @disable_cert_verification
    @unittest_run_loop
    async def test_auth_token_free_request_without_token(self):
        s = TokenSession()
        s.REQUEST_URL = 'https://{}/method/'.format(self.base_url)
        result = await s.send_api_request('users.get', {'user_ids': 1})
        await s.close()
        self.assertListEqual(result, [{'id': 1, 'last_name': 'Дуров', 'first_name': 'Павел'}])

    @disable_cert_verification
    @unittest_run_loop
    async def test_auth_token_request_without_token(self):
        s = TokenSession('token')
        s.REQUEST_URL = 'https://{}/method/'.format(self.base_url)
        with self.assertRaises(VkAuthError):
            await s.send_api_request('users.get.error', {'user_ids': 1})
        await s.close()


class ImplicitSessionTestCase(AioTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Configure mock server.
        cls.mock_server_port = get_free_port()
        cls.mock_server = HTTPServer(('localhost', cls.mock_server_port), VKRequestHandler)
        cls.mock_server.socket = ssl.wrap_socket(cls.mock_server.socket, server_side=True,
                                                 certfile=os.path.join(TEST_DIR, 'certs', 'cert.pem'),
                                                 keyfile=os.path.join(TEST_DIR, 'certs', 'key.pem'))

        # Start running mock server in a separate thread.
        # Daemon threads automatically shut down when the main process exits.
        cls.mock_server_thread = Thread(target=cls.mock_server.serve_forever)
        cls.mock_server_thread.setDaemon(True)
        cls.mock_server_thread.start()
        cls.base_url = 'localhost:{port}'.format(port=cls.mock_server_port)

        cls.json_url = 'https://{}/'.format(cls.base_url)

    @disable_cert_verification
    @unittest_run_loop
    async def test_auth_with_empty_data(self):
        s = ImplicitSession(login='', password='', app_id='')
        s.REQUEST_URL = 'https://{}/method/'.format(self.base_url)
        s.AUTH_URL = 'https://{}/authorize'.format(self.base_url)

        with self.assertRaises(VkAuthError):
            await s.authorize()
        await s.close()

    @disable_cert_verification
    @unittest_run_loop
    async def test_auth_with_2factor(self):
        s = ImplicitSession(login='login', password='pass', app_id='123')
        s.REQUEST_URL = 'https://{}/method/'.format(self.base_url)
        s.AUTH_URL = 'https://{}/authorize'.format(self.base_url)

        await s.authorize()
        await s.close()

    @unittest.skip("TODO add captcha test")
    @disable_cert_verification
    @unittest_run_loop
    async def test_auth_process_captcha_without(self):
        s = ImplicitSession(login='login', password='pass', app_id='123')
        s.REQUEST_URL = 'https://{}/method/'.format(self.base_url)
        s.AUTH_URL = 'https://{}/authorize'.format(self.base_url)

        await s.authorize()
        await s.close()
