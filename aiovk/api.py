from functools import partial


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
        return await self._api._session.send_api_request(
            self._method_name,
            method_args,
            timeout,
        )


class LazyAPI:
    def __init__(self, session):
        self._session = session

    def __getattr__(self, method_name):
        return LazyRequest(self, method_name)

    def __call__(self, method_name, **method_kwargs):
        return getattr(self, method_name)(**method_kwargs)


class LazyRequest:
    __slots__ = ('_api', '_method_name', '_method_args')

    def __init__(self, api, method_name):
        self._api = api
        self._method_name = method_name

    def __getattr__(self, method_name):
        return LazyRequest(self._api, self._method_name + '.' + method_name)

    def __call__(self, **method_args):
        timeout = method_args.pop('timeout', None)
        self._method_args = method_args
        return partial(
            self._api._session.send_api_request,
            self._method_name,
            method_args,
            timeout
        )
