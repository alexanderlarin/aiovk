import asyncio
import json
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Dict, Optional

from . import TokenSession, API


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
    values: dict
    result: AsyncResult

    def get_execute_representation(self) -> str:
        return f"API.{self.method}({json.dumps(self.values)})"


class AsyncVkExecuteRequestPool:
    """Позволяет объединять обращений к api с использованием одного токена
    в группы и выполнять каждую группу обращений за один запрос с использованием
    метода execute"""

    def __init__(self, call_number_per_request=25):
        self.call_number_per_request = call_number_per_request
        self.pool: Dict[str, List[VkCall]] = defaultdict(list)
        self.sessions = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args, **kwargs):
        await self.execute()
        await asyncio.gather(*[session.close() for session in self.sessions])

    async def execute(self):
        """
        Группирует обращения и выполняет их с помощью метода execute, после
        выполнения пул очищается.
        """
        executed_pools = []
        for token, calls in self.pool.items():
            session = TokenSession(token)
            self.sessions.append(session)
            api = API(session)

            for methods_pool in chunks(calls, self.call_number_per_request):
                executed_pools.append(VkExecuteMethodsPool(methods_pool).execute(api))
        await asyncio.gather(*executed_pools)
        self.pool = []

    def call(self, method, token, values=None) -> AsyncResult:
        """
        Добавляет вызов метода api в пул
        :param method: название метода api vk
        :param token: токен для выполнения запроса
        :param values: параметры
        :return: объект, который будет содержать результат после закрытия пула
        """
        if values is None:
            values = {}
        result = AsyncResult()
        self.pool[token].append(VkCall(method=method, values=values, result=result))
        return result


class VkExecuteMethodsPool:
    def __init__(self, pool: Optional[VkCall] = None):
        if not pool:
            pool = []
        self.pool: List[VkCall] = pool

    async def execute(self, api: API):
        """
        Выполняет обращения в pool методом execute и сохраняет результаты
        для каждого обращения
        :param api: объект API для выполнения запроса
        """
        methods = [call.get_execute_representation() for call in self.pool]
        code = f"return [{','.join(methods)}];"
        response = await api.execute(code=code, raw=True)

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
