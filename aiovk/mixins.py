from aiovk.utils import TaskQueue, wait_free_slot


class LimitRateDriverMixin(object):
    requests_per_period = 3
    period = 1  #seconds

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._queue = TaskQueue(self.requests_per_period, self.period)

    @wait_free_slot
    async def json(self, *args, **kwargs):
        return await super().json(*args, **kwargs)

    @wait_free_slot
    async def get_text(self, *args, **kwargs):
        return await super().get_text(*args, **kwargs)

    @wait_free_slot
    async def get_bin(self, *args, **kwargs):
        return await super().get_bin(*args, **kwargs)

    @wait_free_slot
    async def post_text(self, *args, **kwargs):
        return await super().post_text(*args, **kwargs)

    def close(self):
        super().close()
        self._queue.canel()
