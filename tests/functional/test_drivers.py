import json

import proxy
import pytest
from aiohttp import web
from aiohttp.test_utils import unused_port
from python_socks import ProxyType
from yarl import URL

from aiovk.drivers import HttpDriver, ProxyDriver

pytestmark = pytest.mark.asyncio


@pytest.fixture()
def simple_response_data():
    return {'a': 1}


@pytest.fixture()
async def vk_server(aiohttp_server, simple_response_data):
    async def simple_response_data_handler(request):
        return web.json_response(simple_response_data)

    app = web.Application()
    app.add_routes([web.route('*', r'/{name:.*}', simple_response_data_handler)])
    server = await aiohttp_server(app)
    yield server


@pytest.fixture(scope='module')
def proxy_server():
    with proxy.start(['--hostname', '127.0.0.1', '--num-workers', '1', '--port', str(unused_port())]) as p:
        yield p


@pytest.mark.parametrize(
    'driver_class, use_proxy',
    [
        (HttpDriver, False),
        (ProxyDriver, True),
    ]
)
async def test_post_json(simple_response_data, vk_server, proxy_server, driver_class, use_proxy):
    url = f'http://{vk_server.host}:{vk_server.port}/'
    params = {}
    if use_proxy:
        params['address'] = str(proxy_server.flags.hostname)
        params['port'] = proxy_server.flags.port
        params['proxy_type'] = ProxyType.HTTP
    driver = driver_class(**params)
    status, jsn = await driver.post_json(url, {})
    await driver.close()

    assert status == 200
    assert jsn == simple_response_data


@pytest.mark.parametrize(
    'driver_class, use_proxy',
    [
        (HttpDriver, False),
        (ProxyDriver, True),
    ]
)
async def test_get_bin(simple_response_data, vk_server, proxy_server, driver_class, use_proxy):
    url = f'http://{vk_server.host}:{vk_server.port}/'
    params = {}
    if use_proxy:
        params['address'] = str(proxy_server.flags.hostname)
        params['port'] = proxy_server.flags.port
        params['proxy_type'] = ProxyType.HTTP
    driver = driver_class(**params)
    status, text = await driver.get_bin(url, {})
    await driver.close()

    assert status == 200
    assert text == json.dumps(simple_response_data).encode()


@pytest.mark.parametrize(
    'driver_class, use_proxy',
    [
        (HttpDriver, False),
        (ProxyDriver, True),
    ]
)
async def test_get_text(simple_response_data, vk_server, proxy_server, driver_class, use_proxy):
    url = f'http://{vk_server.host}:{vk_server.port}/'
    params = {}
    if use_proxy:
        params['address'] = str(proxy_server.flags.hostname)
        params['port'] = proxy_server.flags.port
        params['proxy_type'] = ProxyType.HTTP
    driver = driver_class(**params)
    status, text, redirect_url = await driver.get_text(url, {})
    await driver.close()

    assert status == 200
    assert text == json.dumps(simple_response_data)
    assert redirect_url == URL(url)


@pytest.mark.parametrize(
    'driver_class, use_proxy',
    [
        (HttpDriver, False),
        (ProxyDriver, True),
    ]
)
async def test_post_text(simple_response_data, vk_server, proxy_server, driver_class, use_proxy):
    data = {
        'login': 'test',
        'password': 'test'
    }
    url = f'http://{vk_server.host}:{vk_server.port}/'
    params = {}
    if use_proxy:
        params['address'] = str(proxy_server.flags.hostname)
        params['port'] = proxy_server.flags.port
        params['proxy_type'] = ProxyType.HTTP
    driver = driver_class(**params)
    status, text, redirect_url = await driver.post_text(url, data=data)
    await driver.close()

    assert status == 200
    assert text == json.dumps(simple_response_data)
    assert redirect_url == URL(url)
