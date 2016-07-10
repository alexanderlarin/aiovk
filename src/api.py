class API:
    def __init__(self, session):
        self._session = session

    def __getattr__(self, method_name):
        return Request(self, method_name)

    async def __call__(self, method_name, **method_kwargs):
        return await getattr(self, method_name)(**method_kwargs)


class Request:
    __slots__ = ('_api', '_method_name', '_method_args')

    def __init__(self, api, method_name):
        self._api = api
        self._method_name = method_name

    def __getattr__(self, method_name):
        return Request(self._api, self._method_name + '.' + method_name)

    async def __call__(self, **method_args):
        timeout = method_args.pop('timeout', None)
        self._method_args = method_args
        return await self._api._session.make_request(self, timeout)
