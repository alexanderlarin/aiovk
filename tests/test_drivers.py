import json
import unittest

import aio.testing
import time

import math

import asyncio

from aiovk.drivers import Socks5Driver, HttpDriver, BaseDriver
from aiovk.mixins import LimitRateDriverMixin
from tests.auth_data import ANON_SOCKS5_ADDRESS, ANON_SOCKS5_PORT, AUTH_SOCKS5_ADDRESS, AUTH_SOCKS5_PORT, \
    AUTH_SOCKS5_LOGIN, AUTH_SOCKS5_PASS


class TestMethodsMixin(object):
    json_url = "https://raw.githubusercontent.com/Fahreeve/aiovk/master/tests/testdata.json"
    json_filepath = "testdata.json"
    driver_kwargs = {}

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
        request_url = "https://github.com/session"
        url, text = await driver.post_text(request_url, data=data)
        driver.close()
        self.assertEqual(url, request_url)
        self.assertEqual(text, 'Cookies must be enabled to use GitHub.')

    @aio.testing.run_until_complete
    def test_post_text_default_loop(self):
        yield from self.post_text()

    @aio.testing.run_until_complete
    def test_post_text_custom_loop(self):
        loop = asyncio.get_event_loop()
        yield from self.post_text(loop)


class HttpDirverTestCase(TestMethodsMixin, unittest.TestCase):
    driver_class = HttpDriver


@unittest.skipIf(not ANON_SOCKS5_ADDRESS or not ANON_SOCKS5_PORT, "you did't enter the anon socks5 data")
class SOCKS5DriverANONTestCase(TestMethodsMixin, unittest.TestCase):
    driver_class = Socks5Driver
    driver_kwargs = {
        "adress": ANON_SOCKS5_ADDRESS,
        "port": ANON_SOCKS5_PORT
    }


@unittest.skipIf(not AUTH_SOCKS5_ADDRESS or not AUTH_SOCKS5_PORT or
                 not AUTH_SOCKS5_LOGIN or not AUTH_SOCKS5_PASS,
                 "you did't enter the auth socks5 data")
class SOCKS5DriverAUTHTestCase(TestMethodsMixin, unittest.TestCase):
    driver_class = Socks5Driver
    driver_kwargs = {
        "adress": ANON_SOCKS5_ADDRESS,
        "port": ANON_SOCKS5_PORT,
        "login": AUTH_SOCKS5_LOGIN,
        "password": AUTH_SOCKS5_PASS
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
