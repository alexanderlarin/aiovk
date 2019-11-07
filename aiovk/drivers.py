import aiohttp

try:
    import aiosocksy
    from aiosocksy.connector import ProxyConnector
except ImportError as e:
    ProxyConnector = None


class BaseDriver:
    def __init__(self, timeout=10, loop=None):
        self.timeout = timeout
        self._loop = loop

    async def post_json(self, url, params, timeout=None):
        """
        :param params: dict of query params
        :return: http status code, dict from json response
        """
        raise NotImplementedError

    async def get_bin(self, url, params, timeout=None):
        """
        :param params: dict of query params
        :return: http status code, binary body of response
        """
        raise NotImplementedError

    async def get_text(self, url, params, timeout=None):
        """
        :param params: dict of query params
        :return: http status code, text body of response and redirect_url
        """
        raise NotImplementedError

    async def post_text(self, url, data, timeout=None):
        """
        :param data: dict pr string
        :return: http status code, text body of response and redirect url
        """
        raise NotImplementedError

    async def close(self):
        raise NotImplementedError


class HttpDriver(BaseDriver):
    def __init__(self, timeout=10, loop=None, session=None):
        super().__init__(timeout, loop)
        if not session:
            self.session = aiohttp.ClientSession(loop=loop)
        else:
            self.session = session

    async def post_json(self, url, params, timeout=None):
        # timeouts - https://docs.aiohttp.org/en/v3.0.0/client_quickstart.html#timeouts
        async with self.session.post(url, data=params, timeout=timeout or self.timeout) as response:
            return response.status, await response.json()

    async def get_bin(self, url, params, timeout=None):
        async with self.session.get(url, params=params, timeout=timeout or self.timeout) as response:
            return response.status, await response.read()

    async def get_text(self, url, params, timeout=None):
        async with self.session.get(url, params=params, timeout=timeout or self.timeout) as response:
            return response.status, await response.text(), response.real_url

    async def post_text(self, url, data, timeout=None):
        async with self.session.post(url, data=data, timeout=timeout or self.timeout) as response:
            return response.status, await response.text(), response.real_url

    async def close(self):
        await self.session.close()


if ProxyConnector:
    class Socks5Driver(HttpDriver):
        connector = ProxyConnector

        def __init__(self, address, port, login=None, password=None, timeout=10, loop=None):
            addr = aiosocksy.Socks5Addr(address, port)
            if login and password:
                auth = aiosocksy.Socks5Auth(login, password=password)
            else:
                auth = None
            conn = self.connector(proxy=addr, proxy_auth=auth, loop=loop)
            session = aiohttp.ClientSession(connector=conn)
            super().__init__(timeout, loop, session)
