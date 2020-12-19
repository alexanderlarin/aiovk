import pytest

from aiovk import ImplicitSession, API, LongPoll, TokenSession

pytestmark = pytest.mark.asyncio


async def test_wait_valid_with_token_session(vk_server, valid_token):
    url = f'http://{vk_server.host}:{vk_server.port}'
    t = TokenSession(valid_token, timeout=1000)
    t.BASE_URL = url
    t.REQUEST_URL = f'{url}/method/'
    api = API(t)
    lp = LongPoll(api, mode=2, wait=2)
    lp.use_https = False

    response = await lp.wait()
    await t.close()
    assert 'ts' in response
    assert 'updates' in response


async def test_wait_valid_with_session_authorised(vk_server):
    url = f'http://{vk_server.host}:{vk_server.port}'
    s = ImplicitSession(login='login', password='pass', app_id='123', scope='messages')
    s.REQUEST_URL = f'{url}/method/'
    s.AUTH_URL = f'{url}/authorize'
    await s.authorize()

    lp = LongPoll(s, mode=2, wait=2)
    lp.use_https = False

    response = await lp.wait()
    await s.close()
    assert 'ts' in response
    assert 'updates' in response


async def test_wait_valid_with_session_auto_auth(vk_server):
    url = f'http://{vk_server.host}:{vk_server.port}'
    s = ImplicitSession(login='login', password='pass', app_id='123', scope='messages')
    s.REQUEST_URL = f'{url}/method/'
    s.AUTH_URL = f'{url}/authorize'

    api = API(s)
    lp = LongPoll(api, mode=2, wait=2)
    lp.use_https = False

    response = await lp.wait()
    await s.close()
    assert 'ts' in response
    assert 'updates' in response
