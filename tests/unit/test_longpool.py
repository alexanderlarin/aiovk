import json

from aiohttp.test_utils import unittest_run_loop

from aiovk import LongPoll, API
from aiovk.drivers import BaseDriver
from aiovk.exceptions import VkLongPollError
from tests.utils import AioTestCase


class TestDriver(BaseDriver):
    counter = 0
    message = None
    original_event = {"type": "group_join", "object": {"user_id": 1, "join_type": "approved"}, "group_id": 1}

    async def get_text(self, url, params, timeout=None):
        second_message = json.dumps({'ts': -TestSession.TS, 'updates': [self.original_event]})
        if self.counter > 5:
            self.counter = 0
            return 200, second_message, url

        self.counter += 1

        if self.message is None:
            return 200, second_message, url

        return 200, json.dumps(self.message), url


class TestSession:
    timeout = 10
    TS = 1
    PTS = 2
    KEY = 'key'
    SERVER = 'localhost'

    driver = TestDriver()

    async def send_api_request(self, method_name: str, params: dict = None, timeout: int = None) -> dict:
        return {"key": self.KEY, "server": self.SERVER, "ts": self.TS, "pts": self.PTS}


class LongPollTestCase(AioTestCase):
    @unittest_run_loop
    async def test_init_with_session(self):
        session = TestSession()
        lp = LongPoll(session, mode=0)
        await lp._get_long_poll_server()

    @unittest_run_loop
    async def test_init_with_api(self):
        session = API(TestSession())
        lp = LongPoll(session, mode=0)
        await lp._get_long_poll_server()

    @unittest_run_loop
    async def test_get_pts_first_call(self):
        session = API(TestSession())
        lp = LongPoll(session, mode=0)
        pts = await lp.get_pts()
        self.assertIsInstance(pts, type(TestSession.PTS))
        self.assertEqual(pts, TestSession.PTS)

    @unittest_run_loop
    async def test_get_pts_cached_value(self):
        session = API(TestSession())
        lp = LongPoll(session, mode=0)
        await lp.get_pts()
        pts = await lp.get_pts()
        self.assertIsInstance(pts, type(TestSession.PTS))
        self.assertEqual(pts, TestSession.PTS)

    @unittest_run_loop
    async def test_get_pts_need_ts(self):
        session = API(TestSession())
        lp = LongPoll(session, mode=0)
        result = await lp.get_pts(need_ts=True)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], TestSession.PTS)
        self.assertEqual(result[1], TestSession.TS)

    @unittest_run_loop
    async def test_wait_valid(self):
        TestDriver.message = {'ts': -TestSession.TS}
        session = API(TestSession())
        lp = LongPoll(session, mode=0)

        response = await lp.wait()
        self.assertDictEqual(response, TestDriver.message)

    @unittest_run_loop
    async def test_wait_error_code_1(self):
        TestDriver.message = {'failed': 1, 'ts': 42}
        session = API(TestSession())
        lp = LongPoll(session, mode=0)

        response = await lp.wait()
        self.assertDictEqual(response, {'ts': -TestSession.TS, 'updates': [TestDriver.original_event]})

    @unittest_run_loop
    async def test_wait_error_code_2(self):
        TestDriver.message = {'failed': 2}
        session = API(TestSession())
        lp = LongPoll(session, mode=0)

        response = await lp.wait()
        self.assertDictEqual(response, {'ts': -TestSession.TS, 'updates': [TestDriver.original_event]})

    @unittest_run_loop
    async def test_wait_error_code_3(self):
        TestDriver.message = {'failed': 3}
        session = API(TestSession())
        lp = LongPoll(session, mode=0)

        response = await lp.wait()
        self.assertDictEqual(response, {'ts': -TestSession.TS, 'updates': [TestDriver.original_event]})

    @unittest_run_loop
    async def test_wait_error_code_4(self):
        TestDriver.message = {'failed': 4}
        session = API(TestSession())
        lp = LongPoll(session, mode=0)

        with self.assertRaises(VkLongPollError):
            await lp.wait()

    @unittest_run_loop
    async def test_iter_valid(self):
        TestDriver.message = None
        session = API(TestSession())
        lp = LongPoll(session, mode=0)

        async for event in lp.iter():
            self.assertDictEqual(event, TestDriver.original_event)
            break

    @unittest_run_loop
    async def test_iter_error_code_1(self):
        TestDriver.message = {'failed': 1, 'ts': 42}
        session = API(TestSession())
        lp = LongPoll(session, mode=0)

        async for event in lp.iter():
            self.assertDictEqual(event, TestDriver.original_event)
            break

    @unittest_run_loop
    async def test_iter_error_code_2(self):
        TestDriver.message = {'failed': 2}
        session = API(TestSession())
        lp = LongPoll(session, mode=0)

        async for event in lp.iter():
            self.assertDictEqual(event, TestDriver.original_event)
            break

    @unittest_run_loop
    async def test_iter_error_code_3(self):
        TestDriver.message = {'failed': 3}
        session = API(TestSession())
        lp = LongPoll(session, mode=0)

        async for event in lp.iter():
            self.assertDictEqual(event, TestDriver.original_event)
            break

    @unittest_run_loop
    async def test_iter_error_code_4(self):
        TestDriver.message = {'failed': 4}
        session = API(TestSession())
        lp = LongPoll(session, mode=0)

        with self.assertRaises(VkLongPollError):
            async for event in lp.iter():
                pass
