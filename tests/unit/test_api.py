import pytest

from aiovk import API
from aiovk.api import Request, LazyRequest, LazyAPI
from aiovk.sessions import BaseSession

pytestmark = pytest.mark.asyncio


class TestSession(BaseSession):
    async def __aenter__(self):
        pass

    async def send_api_request(self, method_name, params=None, timeout=None, raw_response=None):
        out = {
            'method_name': method_name,
            'params': params,
            'timeout': timeout,
        }
        return out


@pytest.mark.parametrize(
    'request_method', [
        'test',
        'test.test',
])
@pytest.mark.parametrize(
    'request_params, timeout', [
        ({}, None),
        ({'arg': 1}, None),
        ({'timeout': 1}, 1),
        ({'arg': 1, 'timeout': 1}, 1),
])
@pytest.mark.parametrize(
    'request_class, is_lazy', [
        (Request, False),
        (LazyRequest, True),
])
@pytest.mark.parametrize(
    'api', [
        API(TestSession()),
        LazyAPI(TestSession()),
    ]
)
async def test_request(api, request_class, request_method, request_params, timeout, is_lazy):
    request = request_class(api, request_method)
    if is_lazy:
        lazy_obj = request(**request_params)
        response = await lazy_obj()
    else:
        response = await request(**request_params)

    params = request_params.copy()
    params.pop('timeout', None)
    expected = {
        'params': params,
        'timeout': timeout,
        'method_name': request_method
    }
    assert response == expected


@pytest.mark.parametrize(
    'request_params, timeout', [
        ({}, None),
        ({'arg': 1}, None),
        ({'timeout': 1}, 1),
        ({'arg': 1, 'timeout': 1}, 1),
])
@pytest.mark.parametrize(
    'method, method_name', [
        (lambda x, **kwargs: x.test(**kwargs), 'test'),
        (lambda x, **kwargs: x.test1.test2(**kwargs), 'test1.test2'),
        (lambda x, **kwargs: x('test', **kwargs), 'test'),
        (lambda x, **kwargs: x('test1.test2', **kwargs), 'test1.test2'),
    ]
)
@pytest.mark.parametrize(
    'api, is_lazy', [
        (LazyAPI(TestSession()), True),
        (API(TestSession()), False),
    ]
)
async def test_api(api, method, request_params, timeout, method_name, is_lazy):
    if is_lazy:
        lazy_obj = method(api, **request_params)
        response = await lazy_obj()
    else:
        response = await method(api, **request_params)

    params = request_params.copy()
    params.pop('timeout', None)
    expected = {
        'params': params,
        'timeout': timeout,
        'method_name': method_name
    }
    assert response == expected
