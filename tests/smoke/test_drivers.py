import json
import os
from http.server import HTTPServer
from threading import Thread
import asyncio
from unittest import IsolatedAsyncioTestCase

from proxy.common.utils import get_available_port
from yarl import URL

import aiovk.drivers as drivers
from tests.utils import AioTestCase, TEST_DIR
from tests.smoke.utils import MockServerRequestHandler


class TestMethodsMixin(IsolatedAsyncioTestCase):
    driver_class = None
    json_filepath = os.path.join(TEST_DIR, 'responses', "testdata.json")
    driver_kwargs = {}

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Configure mock server.
        cls.mock_server_port = get_available_port()
        cls.mock_server = HTTPServer(('localhost', cls.mock_server_port), MockServerRequestHandler)

        # Start running mock server in a separate thread.
        # Daemon threads automatically shut down when the main process exits.
        cls.mock_server_thread = Thread(target=cls.mock_server.serve_forever)
        cls.mock_server_thread.setDaemon(True)
        cls.mock_server_thread.start()

        cls.json_url = 'http://localhost:{port}/'.format(port=cls.mock_server_port)

    async def get_json(self, loop=None):
        driver = self.driver_class(loop=loop, **self.driver_kwargs)
        status, jsn = await driver.post_json(self.json_url, {})
        await driver.close()
        self.assertEqual(status, 200)
        with open(self.json_filepath) as f:
            original = json.load(f)
        self.assertDictEqual(jsn, original)

    async def test_json_default_loop(self):
        await self.get_json()

    async def test_json_custom_loop(self):
        loop = asyncio.get_event_loop()
        await self.get_json(loop)

    async def get_text(self, loop=None):
        driver = self.driver_class(loop=loop, **self.driver_kwargs)
        request_url = self.json_url
        status, text, redirect_url = await driver.get_text(self.json_url, {})
        await driver.close()
        self.assertEqual(status, 200)
        with open(self.json_filepath) as f:
            original = f.read()
        self.assertEqual(text, original)
        self.assertEqual(redirect_url, URL(request_url))

    async def test_get_text_default_loop(self):
        await self.get_text()

    async def test_get_text_custom_loop(self):
        loop = asyncio.get_event_loop()
        await self.get_text(loop)

    async def get_bin(self, loop=None):
        driver = self.driver_class(loop=loop, **self.driver_kwargs)
        status, text = await driver.get_bin(self.json_url, {})
        await driver.close()
        self.assertEqual(status, 200)
        with open(self.json_filepath, 'rb') as f:
            original = f.read()
        self.assertEqual(text, original)

    async def test_get_bin_default_loop(self):
        await self.get_bin()

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
        status, text, redirect_url = await driver.post_text(request_url, data=data)
        await driver.close()

        with open(self.json_filepath) as f:
            expected = f.read()

        self.assertEqual(status, 200)
        self.assertEqual(text, expected)
        self.assertEqual(redirect_url, URL(request_url))

    async def test_post_text_default_loop(self):
        await self.post_text()

    async def test_post_text_custom_loop(self):
        loop = asyncio.get_event_loop()
        await self.post_text(loop)


class HttpDirverTestCase(TestMethodsMixin, AioTestCase):
    driver_class = drivers.HttpDriver


if drivers.ProxyConnector is not None:
    import proxy
    from python_socks import ProxyType


    class ProxyDriverANONTestCase(TestMethodsMixin, proxy.TestCase, IsolatedAsyncioTestCase):
        driver_class = drivers.ProxyDriver

        @property
        def driver_kwargs(self):
            return {
                "address": '127.0.0.1',
                "port": self.PROXY_PORT,
                'proxy_type': ProxyType.HTTP,
            }


    # @mock.patch('aiovk.drivers.ProxyDriver.connector', TestSocksConnector)
    # class ProxyDriverAUTHTestCase(TestMethodsMixin, AioTestCase):
    #     driver_class = drivers.ProxyDriver
    #     driver_kwargs = {
    #         "address": '127.0.0.1',
    #         "port": get_free_port(),
    #         "login": 'test',
    #         "password": 'test'
    #     }
