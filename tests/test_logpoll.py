import json
import unittest

import aio.testing

from aiovk import API, TokenSession
from aiovk.drivers import BaseDriver
from aiovk.exceptions import VkLongPollError
from aiovk.longpoll import LongPoll
from tests.auth_data import USER_LOGIN, USER_PASSWORD, APP_ID
from tests.helpers import TestAuthSession


class TestDriver(BaseDriver):
    counter = 0
    message = {}

    async def get_text(self, url, params, timeout=None):
        if self.counter > 5:
            self.counter = 0
            return 200, json.dumps({'ts': -TestSession.TS})
        self.counter += 1
        return 200, json.dumps(self.message)


class TestSession:
    timeout = 10
    TS = 1
    PTS = 2
    KEY = 'key'
    SERVER = 'localhost'

    driver = TestDriver()

    async def make_request(self, method_request, timeout=None):
        params = method_request._method_args
        out = {'method_name': method_request._method_name,
               'params': params,
               'timeout': timeout,
               'ts': self.TS,
               'pts': self.PTS,
               'key': self.KEY,
               'server': self.SERVER
               }
        return out


class LongPollTestCase(unittest.TestCase):
    @aio.testing.run_until_complete
    def test_init_with_session(self):
        session = TestSession()
        lp = LongPoll(session, mode=0)
        yield from lp._get_long_poll_server()

    @aio.testing.run_until_complete
    def test_init_with_api(self):
        session = API(TestSession())
        lp = LongPoll(session, mode=0)
        yield from lp._get_long_poll_server()

    @aio.testing.run_until_complete
    def test_get_pts_first_call(self):
        session = API(TestSession())
        lp = LongPoll(session, mode=0)
        pts = yield from lp.get_pts()
        self.assertIsInstance(pts, type(TestSession.PTS))
        self.assertEqual(pts, TestSession.PTS)

    @aio.testing.run_until_complete
    def test_get_pts_cached_value(self):
        session = API(TestSession())
        lp = LongPoll(session, mode=0)
        yield from lp.get_pts()
        pts = yield from lp.get_pts()
        self.assertIsInstance(pts, type(TestSession.PTS))
        self.assertEqual(pts, TestSession.PTS)

    @aio.testing.run_until_complete
    def test_get_pts_need_ts(self):
        session = API(TestSession())
        lp = LongPoll(session, mode=0)
        result = yield from lp.get_pts(need_ts=True)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], TestSession.PTS)
        self.assertEqual(result[1], TestSession.TS)

    @aio.testing.run_until_complete
    def test_wait_valid(self):
        TestDriver.message = {'ts': -TestSession.TS}
        session = API(TestSession())
        lp = LongPoll(session, mode=0)

        response = yield from lp.wait()
        self.assertDictEqual(response, TestDriver.message)

    @aio.testing.run_until_complete
    def test_wait_error_code_1(self):
        TestDriver.message = {'failed': 1, 'ts': 42}
        session = API(TestSession())
        lp = LongPoll(session, mode=0)

        response = yield from lp.wait()
        self.assertDictEqual(response, {'ts': -TestSession.TS})

    @aio.testing.run_until_complete
    def test_wait_error_code_2(self):
        TestDriver.message = {'failed': 2}
        session = API(TestSession())
        lp = LongPoll(session, mode=0)

        response = yield from lp.wait()
        self.assertDictEqual(response, {'ts': -TestSession.TS})

    @aio.testing.run_until_complete
    def test_wait_error_code_3(self):
        TestDriver.message = {'failed': 3}
        session = API(TestSession())
        lp = LongPoll(session, mode=0)

        response = yield from lp.wait()
        self.assertDictEqual(response, {'ts': -TestSession.TS})

    @aio.testing.run_until_complete
    def test_wait_error_code_4(self):
        TestDriver.message = {'failed': 4}
        session = API(TestSession())
        lp = LongPoll(session, mode=0)

        with self.assertRaises(VkLongPollError):
            yield from lp.wait()


class LongPollRealTestCase(unittest.TestCase):
    @aio.testing.run_until_complete
    def test_wait_valid_with_token_session(self):
        s = TestAuthSession(login=USER_LOGIN, password=USER_PASSWORD, app_id=APP_ID, scope='messages')
        yield from s.authorize()
        s.close()

        api = API(TokenSession(s.access_token))
        lp = LongPoll(api, mode=2, wait=2)

        response = yield from lp.wait()
        self.assertTrue('ts' in response)
        self.assertTrue('updates' in response)

    @aio.testing.run_until_complete
    def test_wait_valid_with_session_authorised(self):
        s = TestAuthSession(login=USER_LOGIN, password=USER_PASSWORD, app_id=APP_ID, scope='messages')
        yield from s.authorize()

        lp = LongPoll(s, mode=2, wait=2)

        response = yield from lp.wait()
        s.close()
        self.assertTrue('ts' in response)
        self.assertTrue('updates' in response)

    @aio.testing.run_until_complete
    def test_wait_valid_with_session_auto_auth(self):
        s = TestAuthSession(login=USER_LOGIN, password=USER_PASSWORD, app_id=APP_ID, scope='messages')

        api = API(s)
        lp = LongPoll(api, mode=2, wait=2)

        response = yield from lp.wait()
        s.close()
        self.assertTrue('ts' in response)
        self.assertTrue('updates' in response)
