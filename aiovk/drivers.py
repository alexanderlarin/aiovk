import aiohttp
from aiohttp import hdrs
from multidict import CIMultiDict
from multidict import CIMultiDictProxy

try:
    import aiosocks
    from aiosocks.connector import ProxyConnector
except ImportError:
    pass


class CustomClientResponse(aiohttp.ClientResponse):
    # you have to use this class in response_class parameter of any aiohttp.ClientSession instance
    # example: aiohttp.ClientSession(response_class=CustomClientResponse)
    # read more: https://github.com/Fahreeve/aiovk/issues/3

    async def start(self, connection, read_until_eof=False):
        # vk.com return url like this: http://REDIRECT_URI#access_token=...
        # but aiohttp by default removes all parameters after '#'
        await super().start(connection, read_until_eof)
        headers = CIMultiDict(self.headers)
        location = headers.get(hdrs.LOCATION, None)
        if location is not None:
            headers[hdrs.LOCATION] = location.replace('#', '?')
        self.headers = CIMultiDictProxy(headers)
        self.raw_headers = tuple(headers.items())
        return self


class BaseDriver:
    def __init__(self, timeout=10, loop=None):
        self.timeout = timeout
        self._loop = loop

    async def json(self, url, params, timeout=None):
        '''
        :param params: dict of query params
        :return: dict from json response
        '''
        raise NotImplementedError

    async def get_text(self, url, params, timeout=None):
        '''
        :param params: dict of query params
        :return: http status code, text body of response
        '''
        raise NotImplementedError

    async def get_bin(self, url, params, timeout=None):
        '''
        :param params: dict of query params
        :return: http status code, binary body of response
        '''
        raise NotImplementedError

    async def post_text(self, url, data, timeout=None):
        '''
        :param data: dict pr string
        :return: redirect url and text body of response
        '''
        raise NotImplementedError

    def close(self):
        raise NotImplementedError


class HttpDriver(BaseDriver):
    def __init__(self, timeout=10, loop=None):
        super().__init__(timeout, loop)
        self.session = aiohttp.ClientSession(
            response_class=CustomClientResponse, loop=loop)

    async def json(self, url, params, timeout=None):
        with aiohttp.Timeout(timeout or self.timeout):
            async with self.session.get(url, params=params) as response:
                return await response.json()

    async def get_text(self, url, params, timeout=None):
        with aiohttp.Timeout(timeout or self.timeout):
            response = await self.session.get(url, params=params)
            return response.status, await response.text()

    async def get_bin(self, url, params, timeout=None):
        with aiohttp.Timeout(timeout or self.timeout):
            response = await self.session.get(url, params=params)
            return await response.read()

    async def post_text(self, url, data, timeout=None):
        with aiohttp.Timeout(timeout or self.timeout):
            response = await self.session.post(url, data=data)
            return response.url, await response.text()

    def close(self):
        self.session.close()


class Socks5Driver(HttpDriver):
    connector = ProxyConnector

    def __init__(self, address, port, login=None, password=None, timeout=10, loop=None):
        super().__init__(timeout)
        self.close()
        addr = aiosocks.Socks5Addr(address, port)
        if login and password:
            auth = aiosocks.Socks5Auth(login, password=password)
        else:
            auth = None
        conn = self.connector(proxy=addr, proxy_auth=auth, loop=loop)
        self.session = aiohttp.ClientSession(connector=conn, response_class=CustomClientResponse)
