import json
import os
from http.server import HTTPServer
from threading import Thread
from unittest import mock
import asyncio
import aiosocksy
from aiohttp import TCPConnector
from aiohttp.test_utils import unittest_run_loop
from yarl import URL

from aiovk.drivers import Socks5Driver, HttpDriver
from tests.utils import AioTestCase, TEST_DIR
from tests.smoke.utils import get_free_port, MockServerRequestHandler


class TestMethodsMixin:
    driver_class = None
    json_filepath = os.path.join(TEST_DIR, 'responses', "testdata.json")
    driver_kwargs = {}

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Configure mock server.
        cls.mock_server_port = get_free_port()
        cls.mock_server = HTTPServer(('localhost', cls.mock_server_port), MockServerRequestHandler)

        # Start running mock server in a separate thread.
        # Daemon threads automatically shut down when the main process exits.
        cls.mock_server_thread = Thread(target=cls.mock_server.serve_forever)
        cls.mock_server_thread.setDaemon(True)
        cls.mock_server_thread.start()

        cls.json_url = 'http://localhost:{port}/'.format(port=cls.mock_server_port)

    async def json(self, loop=None):
        driver = self.driver_class(loop=loop, **self.driver_kwargs)
        jsn = await driver.json(self.json_url, {})
        await driver.close()
        original = {}
        with open(self.json_filepath) as f:
            original = json.load(f)
        self.assertDictEqual(jsn, original)

    @unittest_run_loop
    async def test_json_default_loop(self):
        await self.json()

    @unittest_run_loop
    async def test_json_custom_loop(self):
        loop = asyncio.get_event_loop()
        await self.json(loop)

    async def get_text(self, loop=None):
        driver = self.driver_class(loop=loop, **self.driver_kwargs)
        status, text = await driver.get_text(self.json_url, {})
        await driver.close()
        self.assertEqual(status, 200)
        original = ''
        with open(self.json_filepath) as f:
            original = f.read()
        self.assertEqual(text, original)

    @unittest_run_loop
    async def test_get_text_default_loop(self):
        await self.get_text()

    @unittest_run_loop
    async def test_get_text_custom_loop(self):
        loop = asyncio.get_event_loop()
        await self.get_text(loop)

    async def get_bin(self, loop=None):
        driver = self.driver_class(loop=loop, **self.driver_kwargs)
        text = await driver.get_bin(self.json_url, {})
        await driver.close()
        original = ''
        with open(self.json_filepath, 'rb') as f:
            original = f.read()
        self.assertEqual(text, original)

    @unittest_run_loop
    async def test_get_bin_default_loop(self):
        await self.get_bin()

    @unittest_run_loop
    async def test_get_bin_custom_loop(self):
        loop = asyncio.get_event_loop()
        await self.get_bin(loop)

    async def post_text(self, loop=None):
        data = {
            "login": 'test',
            "password": "test"
        }
        driver = self.driver_class(loop=loop, **self.driver_kwargs)
        request_url = self.json_url
        url, text = await driver.post_text(request_url, data=data)
        await driver.close()
        self.assertEqual(url, URL(request_url))
        self.assertEqual(text, 'OK')

    @unittest_run_loop
    async def test_post_text_default_loop(self):
        await self.post_text()

    @unittest_run_loop
    async def test_post_text_custom_loop(self):
        loop = asyncio.get_event_loop()
        await self.post_text(loop)


class HttpDirverTestCase(TestMethodsMixin, AioTestCase):
    driver_class = HttpDriver


class TestSocksConnector(TCPConnector):
    def __init__(self, proxy, proxy_auth, loop):
        super().__init__(loop=loop)
        assert type(proxy) == aiosocksy.Socks5Addr
        assert type(proxy_auth) == aiosocksy.Socks5Auth or proxy_auth is None


@mock.patch('aiovk.drivers.Socks5Driver.connector', TestSocksConnector)
class SOCKS5DriverANONTestCase(TestMethodsMixin, AioTestCase):
    driver_class = Socks5Driver
    driver_kwargs = {
        "address": '127.0.0.1',
        "port": get_free_port()
    }


@mock.patch('aiovk.drivers.Socks5Driver.connector', TestSocksConnector)
class SOCKS5DriverAUTHTestCase(TestMethodsMixin, AioTestCase):
    driver_class = Socks5Driver
    driver_kwargs = {
        "address": '127.0.0.1',
        "port": get_free_port(),
        "login": 'test',
        "password": 'test'
    }
