import json

import pytest

from aiovk import LongPoll, API
from aiovk.drivers import BaseDriver
from aiovk.exceptions import VkLongPollError
from aiovk.longpoll import BotsLongPoll
from aiovk.sessions import BaseSession

pytestmark = pytest.mark.asyncio


class Driver(BaseDriver):
    counter = 0
    message = None
    original_event = {"type": "group_join", "object": {"user_id": 1, "join_type": "approved"}, "group_id": 1}
    expected_version = None
    expected_ts = None
    expected_mode = None

    async def get_text(self, url, params, timeout=None):
        message = json.dumps(self.messages[self.counter])
        self.counter += 1
        if self.expected_mode is not None:
            assert params['mode'] == self.expected_mode

        if self.expected_version is not None:
            assert params['version'] == self.expected_version

        if self.expected_ts is not None:
            assert params['ts'] == self.expected_ts

        return 200, message, url


class Session(BaseSession):
    async def __aenter__(self):
        pass

    timeout = 10
    TS = 1
    PTS = 2
    KEY = 'key'
    SERVER = 'superhost'

    def __init__(self):
        self.driver = Driver()

    async def send_api_request(self, *args, **kwargs) -> dict:
        return {"key": self.KEY, "server": self.SERVER, "ts": self.TS, "pts": self.PTS}


@pytest.mark.parametrize(
    'session',
    [
        Session(),
        API(Session())
    ]
)
async def test_longpoll_get_pts(session):
    lp = LongPoll(session, mode=0)
    pts = await lp.get_pts()
    assert pts == Session.PTS


@pytest.mark.parametrize(
    'session',
    [
        Session(),
        API(Session())
    ]
)
async def test_longpoll_get_cached_pts(session):
    lp = LongPoll(session, mode=0)
    await lp.get_pts()
    pts = await lp.get_pts()
    assert pts == Session.PTS


@pytest.mark.parametrize(
    'session',
    [
        Session(),
        API(Session())
    ]
)
async def test_longpoll_get_pts_need_ts(session):
    lp = LongPoll(session, mode=0)
    result = await lp.get_pts(need_ts=True)
    assert len(result) == 2
    assert result[0] == Session.PTS
    assert result[1] == Session.TS


@pytest.mark.parametrize(
    'messages, exception, ts',
    [
        ([{'ts': 23}], None, 23),
        ([{'failed': 1, 'ts': 42}, {'ts': 45, 'updates': [Driver.original_event]}], None, 45),
        ([{'failed': 2}, {'ts': 63, 'updates': [Driver.original_event]}], None, 63),
        ([{'failed': 3}, {'ts': 56, 'updates': [Driver.original_event]}], None, 56),
        ([{'failed': 4}, {'ts': 11, 'updates': [Driver.original_event]}], VkLongPollError, None),
    ]
)
@pytest.mark.parametrize(
    'longpoll',
    [
        lambda session: LongPoll(session, mode=0),
        lambda session: LongPoll(session, mode=1),
        lambda session: LongPoll(session, mode=1, version=1),
        lambda session: BotsLongPoll(session, group_id=1),
        lambda session: BotsLongPoll(session, group_id=1, version=3),
    ]
)
async def test_longpoll_wait(longpoll, messages, exception, ts):
    session = Session()
    session.driver.messages = messages
    session = API(session)
    lp = longpoll(session)
    session._session.driver.expected_mode = lp.base_params.get('mode')
    session._session.driver.expected_version = lp.base_params.get('version')


    if exception is None:
        response = await lp.wait()
        assert response == messages[-1]
        _, real_ts = await lp.get_pts(need_ts=True)
        assert real_ts == ts
    else:
        with pytest.raises(exception):
            await lp.wait()


@pytest.mark.parametrize(
    'messages, exception, ts',
    [
        ([{'failed': 1, 'ts': 42}, {'ts': 45, 'updates': [Driver.original_event]}], None, 45),
        ([{'failed': 2}, {'ts': 63, 'updates': [Driver.original_event]}], None, 63),
        ([{'failed': 3}, {'ts': 56, 'updates': [Driver.original_event]}], None, 56),
        ([{'failed': 4}, {'ts': 11, 'updates': [Driver.original_event]}], VkLongPollError, None),
        ([{'failed': 3}, {'ts': 56, 'updates': [Driver.original_event]},
                         {'ts': 58, 'updates': [Driver.original_event]}], None, 58),
    ]
)
@pytest.mark.parametrize(
    'longpoll',
    [
        lambda session: LongPoll(session, mode=0),
        lambda session: LongPoll(session, mode=1),
        lambda session: LongPoll(session, mode=1, version=1),
        lambda session: BotsLongPoll(session, group_id=1),
        lambda session: BotsLongPoll(session, group_id=1, version=3),
    ]
)
async def test_longpoll_iter(longpoll, messages, exception, ts):
    session = Session()
    session.driver.messages = messages
    session = API(session)
    lp = longpoll(session)
    session._session.driver.expected_mode = lp.base_params.get('mode')
    session._session.driver.expected_version = lp.base_params.get('version')

    if exception is None:
        num_of_iterations = len([m for m in messages if 'updates' in m])
        i = 0
        async for event in lp.iter():
            assert event == messages[-1]['updates'][0]
            i += 1
            if i >= num_of_iterations:
                break
        _, real_ts = await lp.get_pts(need_ts=True)
        assert real_ts == ts
    else:
        with pytest.raises(exception):
            async for _ in lp.iter():
                pass
