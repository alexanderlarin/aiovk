from pathlib import Path

import aiohttp_jinja2
import jinja2
import pytest
from aiohttp import web


@pytest.fixture()
def user_1_data():
    return [{'id': 1, 'first_name': 'Павел', 'last_name': 'Дуров'}]


@pytest.fixture()
def valid_token():
    return 'token'


@pytest.fixture()
async def vk_server(aiohttp_server, user_1_data, valid_token):
    @aiohttp_jinja2.template('authorize_page.jinja2')
    async def authorize(request):
        if 'client_id' in request.query:
            return {'base_url': request.host}
        else:
            raise web.HTTPNotImplemented

    @aiohttp_jinja2.template('blank.jinja2')
    async def blank(request):
        return

    async def longpoolwait(request):
        return web.json_response({'ts': 1857669127, 'updates': []})

    async def user_get_error(request):
        return web.json_response({'error': {'error_code': 5,
                                            'error_msg': 'User authorization failed: invalid access_token (4).',
                                            'request_params': [{'key': 'oauth', 'value': '1'},
                                                               {'key': 'method', 'value': 'users.get'},
                                                               {'key': 'user_ids', 'value': '1'},
                                                               {'key': 'v', 'value': '5.74'}]}})

    async def user_get(request):
        return web.json_response({'response': user_1_data})

    async def get_long_poll_server(request):
        data = await request.post()
        if data.get('access_token') == valid_token:
            return web.json_response(
                {'response': {'key': 'long_pool_key', 'server': f'{request.host}/im1774', 'ts': 1857669095}})
        else:
            return web.json_response({'error': {'error_code': 5,
                                                'error_msg': 'User authorization failed: no access_token passed.',
                                                'request_params': [{'key': 'oauth', 'value': '1'}, {'key': 'method',
                                                                                                    'value': 'messages.getLongPollServer'},
                                                                   {'key': 'need_pts', 'value': '0'},
                                                                   {'key': 'v', 'value': '5.74'}]}})

    async def root(request):
        data = await request.post()
        if data.get('email') == 'login':
            location = request.app.router['blank'].url_for()
            raise web.HTTPFound(location=f'{location}#access_token={valid_token}')
        else:
            response = aiohttp_jinja2.render_template('blank.jinja2', request, None)
            return response

    app = web.Application()
    template_dir = Path(__file__).parent.parent / 'responses'
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(template_dir))
    app.add_routes([
        web.get('/authorize', authorize),
        web.get('/blank.html', blank, name='blank'),
        web.get('/im1774', longpoolwait),
        web.post('/method/users.get.error', user_get_error),
        web.post('/method/users.get', user_get),
        web.post('/method/messages.getLongPollServer', get_long_poll_server),
        web.post('/', root),
    ])
    server = await aiohttp_server(app)
    yield server
