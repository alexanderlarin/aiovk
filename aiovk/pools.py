import asyncio
import json
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Dict, Optional

from aiovk import TokenSession, API
from aiovk.exceptions import VkAuthError


class AsyncResult:
    def __init__(self):
        self._result = None
        self.ready = False
        self.error = None

    @property
    def result(self):
        return self._result

    @result.setter
    def result(self, val):
        self._result = val
        self.ready = True

    @property
    def ok(self):
        return self.ready and not self.error


@dataclass
class VkCall:
    method: str
    method_args: dict
    result: AsyncResult

    def get_execute_representation(self) -> str:
        return f"API.{self.method}({json.dumps(self.method_args, ensure_ascii=False)})"


class AsyncVkExecuteRequestPool:
    """
    Allows concatenation of api calls using one token into groups and execute each group of hits in
    one request using `execute` method
    """

    def __init__(self, call_number_per_request=25, token_session_class=TokenSession):
        self.token_session_class = token_session_class
        self.call_number_per_request = call_number_per_request
        self.pool: Dict[str, List[VkCall]] = defaultdict(list)
        self.sessions = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args, **kwargs):
        await self.execute()

    async def execute(self):
        try:
            await self._execute()
            await asyncio.gather(*[session.close() for session in self.sessions])
        finally:
            self.pool.clear()
            self.sessions.clear()

    async def _execute(self):
        """
        Groups hits and executes them using the execute method, after execution the pool is cleared
        """
        executed_pools = []
        for token, calls in self.pool.items():
            session = self.token_session_class(token)
            self.sessions.append(session)
            api = API(session)

            for methods_pool in chunks(calls, self.call_number_per_request):
                executed_pools.append(VkExecuteMethodsPool(methods_pool).execute(api))
        await asyncio.gather(*executed_pools)

    def add_call(self, method, token, method_args=None) -> AsyncResult:
        """
        Adds an any api method call to the execute pool

        :param method: api vk method name
        :param token: session token
        :param method_args: params
        :return: object that will contain the result after the pool is closed
        """
        if method_args is None:
            method_args = {}

        result = None
        # searching already added calls with equal token, method and values
        for call in self.pool[token]:
            if call.method == method and call.method_args == method_args:
                result = call.result
                break
        if result:
            return result
        result = AsyncResult()
        self.pool[token].append(VkCall(method=method, method_args=method_args, result=result))
        return result


class VkExecuteMethodsPool:
    def __init__(self, pool: Optional[VkCall] = None):
        if not pool:
            pool = []
        self.pool: List[VkCall] = pool

    async def execute(self, api: API):
        """
        Executes calls to the pool using the execute method and stores the results for each call

        :param api: API object to make the request
        """
        methods = [call.get_execute_representation() for call in self.pool]
        code = f"return [{','.join(methods)}];"
        try:
            response = await api.execute(code=code, raw_response=True)
        except VkAuthError as e:
            for call in self.pool:
                call.result.error = {
                    'method': call.method,
                    'error_code': 5,
                    'error_msg': e.description
                }
            return
        errors = response.pop('execute_errors', [])[::-1]
        response = response['response']

        for call, result in zip(self.pool, response):
            if result is False:
                call.result.error = errors.pop()
            else:
                call.result.result = result


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i: i + n]
