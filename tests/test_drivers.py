import json
import unittest

import aio.testing

from aiovk.drivers import Socks5Driver, HttpDriver
from tests.auth_data import ANON_SOCKS5_ADDRESS, ANON_SOCKS5_PORT, AUTH_SOCKS5_ADDRESS, AUTH_SOCKS5_PORT, \
    AUTH_SOCKS5_LOGIN, AUTH_SOCKS5_PASS


class TestMethodsMixin(object):
    json_url = "https://raw.githubusercontent.com/Fahreeve/aiovk/master/tests/testdata.json"
    json_filepath = "testdata.json"

    @aio.testing.run_until_complete
    def test_json(self):
        driver = self.get_driver()
        jsn = yield from driver.json(self.json_url, {})
        driver.close()
        original = {}
        with open(self.json_filepath) as f:
            original = json.load(f)
        self.assertDictEqual(jsn, original)

    @aio.testing.run_until_complete
    def test_get_text(self):
        driver = self.get_driver()
        status, text = yield from driver.get_text(self.json_url, {})
        driver.close()
        self.assertEqual(status, 200)
        original = ''
        with open(self.json_filepath) as f:
            original = f.read()
        self.assertEqual(text, original)

    @aio.testing.run_until_complete
    def test_get_bin(self):
        driver = self.get_driver()
        text = yield from driver.get_bin(self.json_url, {})
        driver.close()
        original = ''
        with open(self.json_filepath, 'rb') as f:
            original = f.read()
        self.assertEqual(text, original)

    @aio.testing.run_until_complete
    def test_post_text(self):
        data = {
            "login": 'test',
            "password": "test"
        }
        driver = self.get_driver()
        request_url = "https://github.com/session"
        url, text = yield from driver.post_text(request_url, data=data)
        driver.close()
        self.assertEqual(url, request_url)
        self.assertEqual(text, 'Cookies must be enabled to use GitHub.')


class HttpDirverTestCase(TestMethodsMixin, unittest.TestCase):
    def get_driver(self):
        return HttpDriver()


@unittest.skipIf(not ANON_SOCKS5_ADDRESS or not ANON_SOCKS5_PORT, "you did't enter the anon socks5 data")
class SOCKS5DriverANONTestCase(TestMethodsMixin, unittest.TestCase):
    def get_driver(self):
        return Socks5Driver(ANON_SOCKS5_ADDRESS, ANON_SOCKS5_PORT)


@unittest.skipIf(not AUTH_SOCKS5_ADDRESS or not AUTH_SOCKS5_PORT or
                 not AUTH_SOCKS5_LOGIN or not AUTH_SOCKS5_PASS,
                 "you did't enter the auth socks5 data")
class SOCKS5DriverAUTHTestCase(TestMethodsMixin, unittest.TestCase):
    def get_driver(self):
        return Socks5Driver(AUTH_SOCKS5_ADDRESS, AUTH_SOCKS5_PORT, AUTH_SOCKS5_LOGIN, AUTH_SOCKS5_PASS)
