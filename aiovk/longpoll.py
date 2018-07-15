import json
from abc import ABC, abstractmethod

from aiovk import API
from aiovk.api import LazyAPI
from aiovk.exceptions import VkLongPollError


class BaseLongPoll(ABC):
    """Interface for all types of Longpoll API"""
    def __init__(self, session_or_api, mode: int or list, wait: int=25, version: int=2, timeout: int=None):
        """
        :param session_or_api: session object or data for creating a new session
        :type session_or_api: BaseSession or API or LazyAPI
        :param mode: additional answer options
        :param wait: waiting period
        :param version: protocol version
        :param timeout: timeout for *.getLongPollServer request in current session
        """
        if isinstance(session_or_api, (API, LazyAPI)):
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

    @abstractmethod
    async def _get_long_poll_server(self, need_pts: bool=False) -> None:
        """Send *.getLongPollServer request and update internal data

        :param need_pts: need return the pts field
        """

    async def wait(self, need_pts=False) -> dict:
        """Send long poll request

        :param need_pts: need return the pts field
        """
        if not self.base_url:
            await self._get_long_poll_server(need_pts)

        params = {
            'ts': self.ts,
            'key': self.key,
        }
        params.update(self.base_params)
        # invalid mimetype from server
        code, response = await self.api._session.driver.get_text(
            self.base_url, params,
            timeout=2 * self.base_params['wait']
        )

        if code == 403:
            raise VkLongPollError(403, 'smth weth wrong', self.base_url + '/', params)

        response = json.loads(response)
        failed = response.get('failed')

        if not failed:
            self.ts = response['ts']
            return response

        if failed == 1:
            self.ts = response['ts']
        elif failed == 4:
            raise VkLongPollError(
                4,
                'An invalid version number was passed in the version parameter',
                self.base_url + '/',
                params
            )
        else:
            self.base_url = None

        return await self.wait()

    async def get_pts(self, need_ts=False):
        if not self.base_url or not self.pts:
            await self._get_long_poll_server(need_pts=True)

        if need_ts:
            return self.pts, self.ts
        return self.pts


class UserLongPoll(BaseLongPoll):
    """Implements https://vk.com/dev/using_longpoll"""

    async def _get_long_poll_server(self, need_pts=False):
        response = await self.api('messages.getLongPollServer', need_pts=int(need_pts), timeout=self.timeout)
        self.pts = response.get('pts')
        self.ts = response['ts']
        self.key = response['key']
        # fucking differences between long poll methods in vk api!
        self.base_url = 'https://{}'.format(response['server'])


class LongPoll(UserLongPoll):
    """Implements https://vk.com/dev/using_longpoll

    This class for backward compatibility
    """

    
class BotsLongPoll(BaseLongPoll):
    """Implements https://vk.com/dev/bots_longpoll"""
    def __init__(self, session_or_api, mode, group_id, wait=25, version=1, timeout=None):
        super().__init__(session_or_api, mode, wait, version, timeout)
        self.group_id = group_id

    async def _get_long_poll_server(self, need_pts=False):
        response = await self.api('groups.getLongPollServer', group_id=self.group_id)
        self.pts = response.get('pts')
        self.ts = response['ts']
        self.key = response['key']
        self.base_url = '{}'.format(response['server'])  # Method already returning url with https://
