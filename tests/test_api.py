import unittest
import aio.testing
from src.api import API, Request


class TestSession:
    async def make_request(self, method_request, timeout=None):
        params = method_request._method_args
        out = {'method_name': method_request._method_name,
               'params': params,
               'timeout': timeout,
               }
        return out


class RequestTestCase(unittest.TestCase):
    @aio.testing.run_until_complete
    def test_request_without_args(self):
        api = API(TestSession())
        request = Request(api, 'test')
        first = yield from request()
        second = {'params': {},
                  'timeout': None,
                  'method_name': 'test'
                  }
        self.assertDictEqual(first, second)

    @aio.testing.run_until_complete
    def test_request_with_args(self):
        api = API(TestSession())
        request = Request(api, 'test')
        first = yield from request(arg=1)
        second = {'params': {'arg': 1},
                  'timeout': None,
                  'method_name': 'test'
                  }
        self.assertDictEqual(first, second)

    @aio.testing.run_until_complete
    def test_request_with_timeout(self):
        api = API(TestSession())
        request = Request(api, 'test')
        first = yield from request(timeout=1)
        second = {'params': {},
                  'timeout': 1,
                  'method_name': 'test'
                  }
        self.assertDictEqual(first, second)


class APITestCase(unittest.TestCase):
    @aio.testing.run_until_complete
    def test_request_without_args(self):
        api = API(TestSession())
        first = yield from api.test()
        second = {'params': {},
                  'timeout': None,
                  'method_name': 'test'
                  }
        self.assertDictEqual(first, second)

    @aio.testing.run_until_complete
    def test_request_with_args(self):
        api = API(TestSession())
        first = yield from api.test(arg=1)
        second = {'params': {'arg': 1},
                  'timeout': None,
                  'method_name': 'test'
                  }
        self.assertDictEqual(first, second)

    @aio.testing.run_until_complete
    def test_request_with_timeout(self):
        api = API(TestSession())
        first = yield from api.test(timeout=1)
        second = {'params': {},
                  'timeout': 1,
                  'method_name': 'test'
                  }
        self.assertDictEqual(first, second)

    @aio.testing.run_until_complete
    def test_complex_request_without_args(self):
        api = API(TestSession())
        first = yield from api.test1.test2()
        second = {'params': {},
                  'timeout': None,
                  'method_name': 'test1.test2'
                  }
        self.assertDictEqual(first, second)

    @aio.testing.run_until_complete
    def test_complex_request_with_args(self):
        api = API(TestSession())
        first = yield from api.test1.test2(arg=1)
        second = {'params': {'arg': 1},
                  'timeout': None,
                  'method_name': 'test1.test2'
                  }
        self.assertDictEqual(first, second)

    @aio.testing.run_until_complete
    def test_complex_request(self):
        api = API(TestSession())
        first = yield from api.test1.test2(timeout=1)
        second = {'params': {},
                  'timeout': 1,
                  'method_name': 'test1.test2'
                  }
        self.assertDictEqual(first, second)

    @aio.testing.run_until_complete
    def test_request_with_method_name(self):
        api = API(TestSession())
        first = yield from api('test')
        second = {'params': {},
                  'timeout': None,
                  'method_name': 'test'
                  }
        self.assertDictEqual(first, second)

    @aio.testing.run_until_complete
    def test_request_with_method_name_and_args(self):
        api = API(TestSession())
        first = yield from api('test', arg=1)
        second = {'params': {'arg': 1},
                  'timeout': None,
                  'method_name': 'test'
                  }
        self.assertDictEqual(first, second)

    @aio.testing.run_until_complete
    def test_request_with_method_name_and_timeout(self):
        api = API(TestSession())
        first = yield from api('test', timeout=1)
        second = {'params': {},
                  'timeout': 1,
                  'method_name': 'test'
                  }
        self.assertDictEqual(first, second)
