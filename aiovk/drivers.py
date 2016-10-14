import aiohttp
try:
    import aiosocks
    from aiosocks.connector import SocksConnector
except ImportError:
    pass


class BaseDriver:
    def __init__(self, timeout=10):
        self.timeout = timeout

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
    def __init__(self, timeout=10):
        super().__init__(timeout)
        self.session = aiohttp.ClientSession()

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
    def __init__(self, adress, port, login=None, password=None, timeout=10):
        super().__init__(timeout)
        self.close()
        addr = aiosocks.Socks5Addr(adress, port)
        if login and password:
            auth = aiosocks.Socks5Auth(login, password=password)
        else:
            auth = None
        conn = SocksConnector(proxy=addr, proxy_auth=auth)
        self.session = aiohttp.ClientSession(connector=conn)
