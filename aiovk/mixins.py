from aiovk.drivers import BaseDriver
from aiovk.shaping import TaskQueue, wait_free_slot


class LimitRateDriverMixin(BaseDriver):
    def __init__(self, *args, requests_per_period=3, period=1, **kwargs):
        super().__init__(*args, **kwargs)
        self._queue = TaskQueue(requests_per_period, period)

    @wait_free_slot
    async def post_json(self, *args, **kwargs):
        return await super().post_json(*args, **kwargs)

    @wait_free_slot
    async def get_bin(self, *args, **kwargs):
        return await super().get_bin(*args, **kwargs)

    @wait_free_slot
    async def get_text(self, *args, **kwargs):
        return await super().get_text(*args, **kwargs)

    @wait_free_slot
    async def post_text(self, *args, **kwargs):
        return await super().post_text(*args, **kwargs)

    async def close(self):
        await super().close()
        self._queue.cancel()


class SimpleImplicitSessionMixin:
    """
    Simple implementation of processing captcha and 2factor authorization
    """

    async def enter_captcha(self, url, sid):
        bytes = await self.driver.get_bin(url, {})
        with open('captcha.jpg', 'wb') as f:
            f.write(bytes)
        return input("Enter captcha: ")

    async def enter_confirmation_сode(self):
        return input('Enter confirmation сode: ')
