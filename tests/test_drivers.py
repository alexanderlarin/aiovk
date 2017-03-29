import json
import os
import unittest
from http.server import HTTPServer
from threading import Thread
from unittest import mock
import aio.testing
import time
import math
import asyncio
import aiosocks
from aiohttp import TCPConnector
from yarl import URL

from aiovk.drivers import Socks5Driver, HttpDriver, BaseDriver
from aiovk.mixins import LimitRateDriverMixin
from tests.helpers import get_free_port, MockServerRequestHandler


class TestMethodsMixin(object):
    json_filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "testdata.json")
    driver_kwargs = {}

    @classmethod
    def setUpClass(cls):
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
        driver.close()
        original = {}
        with open(self.json_filepath) as f:
            original = json.load(f)
        self.assertDictEqual(jsn, original)

    @aio.testing.run_until_complete
    def test_json_default_loop(self):
        yield from self.json()

    @aio.testing.run_until_complete
    def test_json_custom_loop(self):
        loop = asyncio.get_event_loop()
        yield from self.json(loop)

    async def get_text(self, loop=None):
        driver = self.driver_class(loop=loop, **self.driver_kwargs)
        status, text = await driver.get_text(self.json_url, {})
        driver.close()
        self.assertEqual(status, 200)
        original = ''
        with open(self.json_filepath) as f:
            original = f.read()
        self.assertEqual(text, original)

    @aio.testing.run_until_complete
    def test_get_text_default_loop(self):
        yield from self.get_text()

    @aio.testing.run_until_complete
    def test_get_text_custom_loop(self):
        loop = asyncio.get_event_loop()
        yield from self.get_text(loop)

    async def get_bin(self, loop=None):
        driver = self.driver_class(loop=loop, **self.driver_kwargs)
        text = await driver.get_bin(self.json_url, {})
        driver.close()
        original = ''
        with open(self.json_filepath, 'rb') as f:
            original = f.read()
        self.assertEqual(text, original)

    @aio.testing.run_until_complete
    def test_get_bin_default_loop(self):
        yield from self.get_bin()

    @aio.testing.run_until_complete
    def test_get_bin_custom_loop(self):
        loop = asyncio.get_event_loop()
        yield from self.get_bin(loop)

    async def post_text(self, loop=None):
        data = {
            "login": 'test',
            "password": "test"
        }
        driver = self.driver_class(loop=loop, **self.driver_kwargs)
        request_url = self.json_url
        url, text = await driver.post_text(request_url, data=data)
        driver.close()
        self.assertEqual(url, URL(request_url))
        self.assertEqual(text, 'OK')

    @aio.testing.run_until_complete
    def test_post_text_default_loop(self):
        yield from self.post_text()

    @aio.testing.run_until_complete
    def test_post_text_custom_loop(self):
        loop = asyncio.get_event_loop()
        yield from self.post_text(loop)


class HttpDirverTestCase(TestMethodsMixin, unittest.TestCase):
    driver_class = HttpDriver


class TestSocksConnector(TCPConnector):
    def __init__(self, proxy, proxy_auth, loop):
        super().__init__(loop=loop)
        assert type(proxy) == aiosocks.Socks5Addr
        assert type(proxy_auth) == aiosocks.Socks5Auth or proxy_auth is None


@mock.patch('aiovk.drivers.Socks5Driver.connector', TestSocksConnector)
class SOCKS5DriverANONTestCase(TestMethodsMixin, unittest.TestCase):
    driver_class = Socks5Driver
    driver_kwargs = {
        "address": '127.0.0.1',
        "port": get_free_port()
    }


@mock.patch('aiovk.drivers.Socks5Driver.connector', TestSocksConnector)
class SOCKS5DriverAUTHTestCase(TestMethodsMixin, unittest.TestCase):
    driver_class = Socks5Driver
    driver_kwargs = {
        "address": '127.0.0.1',
        "port": get_free_port(),
        "login": 'test',
        "password": 'test'
    }


class LimitRateBaseTestDriver(BaseDriver):
    async def json(self, *args, **kwargs):
        return time.time()

    def close(self):
        pass


class LimitRateTestDriver(LimitRateDriverMixin, LimitRateBaseTestDriver):
    period = 1
    requests_per_period = 1


class LimitRateDriverMixinTestCase(unittest.TestCase):
    period = 1
    requests_per_period = 1

    def get_driver(self):
        return LimitRateTestDriver()

    @aio.testing.run_until_complete
    def test_json_fast(self):
        driver = self.get_driver()
        t0 = time.time()
        t1 = yield from driver.json()
        self.assertEqual(math.floor(t1 - t0), 0)
        driver.close()

    @aio.testing.run_until_complete
    def test_json_slow(self):
        driver = self.get_driver()
        t1 = yield from driver.json()
        t2 = yield from driver.json()
        self.assertEqual(math.floor(t2 - t1), self.period)
        driver.close()
