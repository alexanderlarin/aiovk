import asyncio


class TaskQueue(asyncio.Queue):
    def __init__(self, max_size, period, *args, **kwargs):
        super().__init__(max_size, *args, **kwargs)
        self.period = period

    def _init(self, maxsize):
        super()._init(maxsize)
        for i in range(maxsize):
            self._queue.append(1)
        self.task = asyncio.ensure_future(self.dispatcher(maxsize))

    async def dispatcher(self, maxsize):
        while True:
            await asyncio.sleep(self.period)
            for i in range(maxsize - self.qsize()):
                self.put_nowait(1)

    def canel(self):
        self.task.cancel()


def wait_free_slot(func):
    async def wrapper(self, *args, **kwargs):
        await self._queue.get()
        return await func(self, *args, **kwargs)
    return wrapper


def get_request_params(request_params):
    return {param['key']: param['value'] for param in request_params}
