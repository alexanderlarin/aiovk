import pytest

from aiovk import ImplicitSession, TokenSession
from aiovk.exceptions import VkAuthError

pytestmark = pytest.mark.asyncio


async def test_token_session_auth_with_empty_token(vk_server):
    s = TokenSession()
    with pytest.raises(VkAuthError):
        await s.authorize()
    await s.close()


async def test_token_session_auth_with_token(vk_server):
    s = TokenSession('token')
    with pytest.raises(VkAuthError):
        await s.authorize()
    await s.close()


async def test_token_session_auth_token_free_request_without_token(vk_server, user_1_data):
    url = f'http://{vk_server.host}:{vk_server.port}'
    s = TokenSession()
    s.REQUEST_URL = f'{url}/method/'
    result = await s.send_api_request('users.get', {'user_ids': 1})
    await s.close()
    assert result == user_1_data


async def test_token_session_auth_token_request_without_token(vk_server):
    url = f'http://{vk_server.host}:{vk_server.port}'
    s = TokenSession('token')
    s.REQUEST_URL = f'{url}/method/'
    with pytest.raises(VkAuthError):
        await s.send_api_request('users.get.error', {'user_ids': 1})
    await s.close()


async def test_implicit_session_auth_with_empty_data(vk_server):
    url = f'http://{vk_server.host}:{vk_server.port}'
    s = ImplicitSession(login='', password='', app_id='')
    s.REQUEST_URL = f'{url}/method/'
    s.AUTH_URL = f'{url}/authorize'

    with pytest.raises(VkAuthError):
        await s.authorize()
    await s.close()


async def test_implicit_session_auth_with_2factor(vk_server):
    url = f'http://{vk_server.host}:{vk_server.port}'
    s = ImplicitSession(login='login', password='pass', app_id='123')
    s.REQUEST_URL = f'{url}/method/'
    s.AUTH_URL = f'{url}/authorize'

    await s.authorize()
    await s.close()


@pytest.mark.skip('TODO add captcha test')
async def test_implicit_session_auth_process_captcha_without(vk_server):
    url = f'http://{vk_server.host}:{vk_server.port}'
    s = ImplicitSession(login='login', password='pass', app_id='123')
    s.REQUEST_URL = f'{url}/method/'
    s.AUTH_URL = f'{url}/authorize'

    await s.authorize()
    await s.close()
