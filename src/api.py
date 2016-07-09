import logging
import aiohttp

logger = logging.getLogger('vk')


class API:
    API_URL = 'https://api.vk.com/method/'
    API_VERSION = '5.52'
    timeout = 10  # sec

    def __init__(self, access_token=None):
        self.access_token = access_token
        headers = {'Accept': 'application/json',
                   'Content-Type': 'application/x-www-form-urlencoded'}
        self.session = aiohttp.ClientSession(headers=headers)

    async def send_request(self, method, kwargs):
        response = await self.fetch(self.API_URL + method, kwargs)
        a = 1

    async def fetch(self, url, params):
        with aiohttp.Timeout(self.timeout):
            async with self.session.get(url, params=params) as response:
                return await response.json()
