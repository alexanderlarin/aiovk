from aiohttp.test_utils import unittest_run_loop

from aiovk import API
from aiovk.api import Request, LazyRequest, LazyAPI
from tests.utils import AioTestCase


class TestSession:
    async def send_api_request(self, method_name, params=None, timeout=None):
        out = {'method_name': method_name,
               'params': params,
               'timeout': timeout,
               }
        return out


class RequestTestCase(AioTestCase):
    @unittest_run_loop
    async def test_request_without_args(self):
        api = API(TestSession())
        request = Request(api, 'test')
        first = await request()
        second = {'params': {},
                  'timeout': None,
                  'method_name': 'test'
                  }
        self.assertDictEqual(first, second)

    @unittest_run_loop
    async def test_request_with_args(self):
        api = API(TestSession())
        request = Request(api, 'test')
        first = await request(arg=1)
        second = {'params': {'arg': 1},
                  'timeout': None,
                  'method_name': 'test'
                  }
        self.assertDictEqual(first, second)

    @unittest_run_loop
    async def test_request_with_timeout(self):
        api = API(TestSession())
        request = Request(api, 'test')
        first = await request(timeout=1)
        second = {'params': {},
                  'timeout': 1,
                  'method_name': 'test'
                  }
        self.assertDictEqual(first, second)


class LazyRequestTestCase(AioTestCase):
    @unittest_run_loop
    async def test_request_without_args(self):
        api = API(TestSession())
        request = LazyRequest(api, 'test')
        message = request()
        first = await message()
        second = {'params': {},
                  'timeout': None,
                  'method_name': 'test'
                  }
        self.assertDictEqual(first, second)

    @unittest_run_loop
    async def test_request_with_args(self):
        api = API(TestSession())
        request = LazyRequest(api, 'test')
        message = request(arg=1)
        first = await message()
        second = {'params': {'arg': 1},
                  'timeout': None,
                  'method_name': 'test'
                  }
        self.assertDictEqual(first, second)

    @unittest_run_loop
    async def test_request_with_timeout(self):
        api = API(TestSession())
        request = LazyRequest(api, 'test')
        message = request(timeout=1)
        first = await message()
        second = {'params': {},
                  'timeout': 1,
                  'method_name': 'test'
                  }
        self.assertDictEqual(first, second)


class APITestCase(AioTestCase):
    @unittest_run_loop
    async def test_request_without_args(self):
        api = API(TestSession())
        first = await api.test()
        second = {'params': {},
                  'timeout': None,
                  'method_name': 'test'
                  }
        self.assertDictEqual(first, second)

    @unittest_run_loop
    async def test_request_with_args(self):
        api = API(TestSession())
        first = await api.test(arg=1)
        second = {'params': {'arg': 1},
                  'timeout': None,
                  'method_name': 'test'
                  }
        self.assertDictEqual(first, second)

    @unittest_run_loop
    async def test_request_with_timeout(self):
        api = API(TestSession())
        first = await api.test(timeout=1)
        second = {'params': {},
                  'timeout': 1,
                  'method_name': 'test'
                  }
        self.assertDictEqual(first, second)

    @unittest_run_loop
    async def test_complex_request_without_args(self):
        api = API(TestSession())
        first = await api.test1.test2()
        second = {'params': {},
                  'timeout': None,
                  'method_name': 'test1.test2'
                  }
        self.assertDictEqual(first, second)

    @unittest_run_loop
    async def test_complex_request_with_args(self):
        api = API(TestSession())
        first = await api.test1.test2(arg=1)
        second = {'params': {'arg': 1},
                  'timeout': None,
                  'method_name': 'test1.test2'
                  }
        self.assertDictEqual(first, second)

    @unittest_run_loop
    async def test_complex_request(self):
        api = API(TestSession())
        first = await api.test1.test2(timeout=1)
        second = {'params': {},
                  'timeout': 1,
                  'method_name': 'test1.test2'
                  }
        self.assertDictEqual(first, second)

    @unittest_run_loop
    async def test_request_with_method_name(self):
        api = API(TestSession())
        first = await api('test')
        second = {'params': {},
                  'timeout': None,
                  'method_name': 'test'
                  }
        self.assertDictEqual(first, second)

    @unittest_run_loop
    async def test_request_with_method_name_and_args(self):
        api = API(TestSession())
        first = await api('test', arg=1)
        second = {'params': {'arg': 1},
                  'timeout': None,
                  'method_name': 'test'
                  }
        self.assertDictEqual(first, second)

    @unittest_run_loop
    async def test_request_with_method_name_and_timeout(self):
        api = API(TestSession())
        first = await api('test', timeout=1)
        second = {'params': {},
                  'timeout': 1,
                  'method_name': 'test'
                  }
        self.assertDictEqual(first, second)


class LazyAPITestCase(AioTestCase):
    @unittest_run_loop
    async def test_request_without_args(self):
        api = LazyAPI(TestSession())
        message = api.test()
        first = await message()
        second = {'params': {},
                  'timeout': None,
                  'method_name': 'test'
                  }
        self.assertDictEqual(first, second)

    @unittest_run_loop
    async def test_request_as_non_lazy_api(self):
        api = LazyAPI(TestSession())
        with self.assertRaises(TypeError):
            await api.test()

    @unittest_run_loop
    async def test_request_with_args(self):
        api = LazyAPI(TestSession())
        message = api.test(arg=1)
        first = await message()
        second = {'params': {'arg': 1},
                  'timeout': None,
                  'method_name': 'test'
                  }
        self.assertDictEqual(first, second)

    @unittest_run_loop
    async def test_request_with_timeout(self):
        api = LazyAPI(TestSession())
        message = api.test(timeout=1)
        first = await message()
        second = {'params': {},
                  'timeout': 1,
                  'method_name': 'test'
                  }
        self.assertDictEqual(first, second)

    @unittest_run_loop
    async def test_complex_request_without_args(self):
        api = LazyAPI(TestSession())
        message = api.test1.test2()
        first = await message()
        second = {'params': {},
                  'timeout': None,
                  'method_name': 'test1.test2'
                  }
        self.assertDictEqual(first, second)

    @unittest_run_loop
    async def test_complex_request_with_args(self):
        api = LazyAPI(TestSession())
        message = api.test1.test2(arg=1)
        first = await message()
        second = {'params': {'arg': 1},
                  'timeout': None,
                  'method_name': 'test1.test2'
                  }
        self.assertDictEqual(first, second)

    @unittest_run_loop
    async def test_complex_request(self):
        api = LazyAPI(TestSession())
        message = api.test1.test2(timeout=1)
        first = await message()
        second = {'params': {},
                  'timeout': 1,
                  'method_name': 'test1.test2'
                  }
        self.assertDictEqual(first, second)

    @unittest_run_loop
    async def test_request_with_method_name(self):
        api = LazyAPI(TestSession())
        message = api('test')
        first = await message()
        second = {'params': {},
                  'timeout': None,
                  'method_name': 'test'
                  }
        self.assertDictEqual(first, second)

    @unittest_run_loop
    async def test_request_with_method_name_and_args(self):
        api = LazyAPI(TestSession())
        message = api('test', arg=1)
        first = await message()
        second = {'params': {'arg': 1},
                  'timeout': None,
                  'method_name': 'test'
                  }
        self.assertDictEqual(first, second)

    @unittest_run_loop
    async def test_request_with_method_name_and_timeout(self):
        api = LazyAPI(TestSession())
        message = api('test', timeout=1)
        first = await message()
        second = {'params': {},
                  'timeout': 1,
                  'method_name': 'test'
                  }
        self.assertDictEqual(first, second)
