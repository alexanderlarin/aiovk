import json

from aiovk import API
from aiovk.exceptions import VkLongPollError


class LongPoll:
    def __init__(self, session_or_api, mode, wait=25, version=1, timeout=None):
        if type(session_or_api) == API:
            self.api = session_or_api
        else:
            self.api = API(session_or_api)
        self.timeout = timeout or self.api._session.timeout
        if type(mode) == list:
            mode = sum(mode)
        self.base_params = {
            'version': version,
            'wait': wait,
            'mode': mode,
            'act': 'a_check'
        }
        self.pts = None
        self.ts = None
        self.key = None
        self.base_url = None

    async def _get_long_poll_server(self, need_pts=False):
        response = await self.api('messages.getLongPollServer', need_pts=int(need_pts), timeout=self.timeout)
        self.pts = response.get('pts')
        self.ts = response['ts']
        self.key = response['key']
        self.base_url = 'https://{}'.format(response['server'])

    async def wait(self, need_pts=False):
        if self.base_url is None:
            await self._get_long_poll_server(need_pts)
        params = {
            'ts': self.ts,
            'key': self.key,
        }
        params.update(self.base_params)
        # invalid mymetype from server
        code, response = await self.api._session.driver.get_text(self.base_url, params, timeout=2*self.base_params['wait'])
        if code == 403:
            raise VkLongPollError(403,
                                  'smth weth wrong',
                                  self.base_url + '/',
                                  params
                                  )
        response = json.loads(response)
        failed = response.get('failed')
        if failed is None:
            self.ts = response['ts']
            return response
        if failed == 1:
            self.ts = response['ts']
        elif failed == 4:
            raise VkLongPollError(4,
                                  'An invalid version number was passed in the version parameter',
                                  self.base_url + '/',
                                  params)
        else:
            self.base_url = None
        return await self.wait()

    async def get_pts(self, need_ts=False):
        if self.base_url is None or self.pts is None:
            await self._get_long_poll_server(need_pts=True)
        if need_ts:
            return self.pts, self.ts
        return self.pts
