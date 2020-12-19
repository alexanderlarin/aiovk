import os
from unittest import IsolatedAsyncioTestCase

# from dotenv import load_dotenv

from aiovk.pools import AsyncResult, AsyncVkExecuteRequestPool

# load_dotenv(
#     os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env")
# )
token1 = os.getenv('TEST_TOKEN_1')
token2 = os.getenv('TEST_TOKEN_2')


# TODO need refactoring
class ExecutePoolTestCase(IsolatedAsyncioTestCase):
    async def test_one_call_per_request(self):
        async with AsyncVkExecuteRequestPool() as pool:
            result = pool.add_call('users.get', token1, {'user_ids': 1})
            self.assertIsInstance(result, AsyncResult)
        self.assertIsNotNone(result.result)
        self.assertEqual(1, result.result[0]['id'])

        async with AsyncVkExecuteRequestPool() as pool:
            result = pool.add_call('users.get', token1, {'user_ids': 1})
            self.assertIsInstance(result, AsyncResult)
            result2 = pool.add_call('users.get', token2, {'user_ids': 2})
            self.assertIsInstance(result2, AsyncResult)

        self.assertTrue(result.ok)
        self.assertIsNotNone(result.result)
        self.assertEqual(1, result.result[0]['id'])
        self.assertTrue(result2.ok)
        self.assertIsNotNone(result2.result)
        self.assertEqual(2, result2.result[0]['id'])

    async def test_less_or_equal_than_25_calls_per_token(self):
        users = []
        async with AsyncVkExecuteRequestPool() as pool:
            for i in range(1, 2):
                result = pool.add_call('users.get', token1, {'user_ids': i})
                users.append(result)
                self.assertIsInstance(result, AsyncResult)

        for i, result in enumerate(users, start=1):
            self.assertTrue(result.ok)
            self.assertIsNotNone(result.result)
            self.assertEqual(i, result.result[0]['id'])

        users = []
        async with AsyncVkExecuteRequestPool() as pool:
            for i in range(1, 25):
                result = pool.add_call('users.get', token1, {'user_ids': i})
                users.append(result)
                self.assertIsInstance(result, AsyncResult)

        for i, result in enumerate(users, start=1):
            self.assertTrue(result.ok)
            self.assertIsNotNone(result.result)
            self.assertEqual(i, result.result[0]['id'])

        users = []
        async with AsyncVkExecuteRequestPool() as pool:
            for i in range(1, 26):
                result = pool.add_call('users.get', token1, {'user_ids': i})
                users.append(result)
                self.assertIsInstance(result, AsyncResult)

            for i in range(26, 51):
                result = pool.add_call('users.get', token2, {'user_ids': i})
                users.append(result)
                self.assertIsInstance(result, AsyncResult)

        for i, result in enumerate(users, start=1):
            self.assertTrue(result.ok)
            self.assertIsNotNone(result.result)
            self.assertEqual(i, result.result[0]['id'])

    async def test_greater_than_25_calls_per_token(self):
        users = []
        async with AsyncVkExecuteRequestPool() as pool:
            for i in range(1, 26):
                result = pool.add_call('users.get', token1, {'user_ids': i})
                users.append(result)
                self.assertIsInstance(result, AsyncResult)

        for i, result in enumerate(users, start=1):
            self.assertTrue(result.ok)
            self.assertIsNotNone(result.result)
            self.assertEqual(i, result.result[0]['id'])

        users = []
        async with AsyncVkExecuteRequestPool() as pool:
            for i in range(1, 50):
                result = pool.add_call('users.get', token1, {'user_ids': i})
                users.append(result)
                self.assertIsInstance(result, AsyncResult)

        for i, result in enumerate(users, start=1):
            self.assertTrue(result.ok)
            self.assertIsNotNone(result.result)
            self.assertEqual(i, result.result[0]['id'])

        users = []
        async with AsyncVkExecuteRequestPool() as pool:
            for i in range(1, 51):
                result = pool.add_call('users.get', token1, {'user_ids': i})
                users.append(result)
                self.assertIsInstance(result, AsyncResult)

            for i in range(51, 99):
                result = pool.add_call('users.get', token2, {'user_ids': i})
                users.append(result)
                self.assertIsInstance(result, AsyncResult)

        for i, result in enumerate(users, start=1):
            self.assertTrue(result.ok)
            self.assertIsNotNone(result.result)
            self.assertEqual(i, result.result[0]['id'])

    async def test_error_requests(self):
        async with AsyncVkExecuteRequestPool() as pool:
            error_result = pool.add_call('users.get', token1, {'user_ids': -1})
            self.assertIsInstance(error_result, AsyncResult)

        self.assertFalse(error_result.ok)
        self.assertIsNone(error_result.result)
        self.assertIsNotNone(error_result.error)
        self.assertDictEqual({
            'method': 'users.get', 'error_code': 113, 'error_msg': 'Invalid user id'
        }, error_result.error)

        async with AsyncVkExecuteRequestPool() as pool:
            error_result = pool.add_call('users.get', token1, {'user_ids': -1})
            success_result = pool.add_call('users.get', token2, {'user_ids': 1})

        self.assertFalse(error_result.ok)
        self.assertIsNone(error_result.result)
        self.assertIsNotNone(error_result.error)
        self.assertDictEqual({
            'method': 'users.get', 'error_code': 113, 'error_msg': 'Invalid user id'
        }, error_result.error)

        self.assertTrue(success_result.ok)
        self.assertIsNotNone(success_result.result)
        self.assertEqual(1, success_result.result[0]['id'])

    async def test_request_without_values(self):
        async with AsyncVkExecuteRequestPool() as pool:
            result = pool.add_call('users.get', token1)
        self.assertTrue(result.ok)
        self.assertIsNotNone(result.result)

    async def test_false_cast_response(self):
        async with AsyncVkExecuteRequestPool() as pool:
            result = pool.add_call("groups.isMember", token1, {"user_id": 1, "group_id": 1})
        self.assertTrue(result.ok)
        self.assertIsNotNone(result.result)
        self.assertEqual(0, result.result)

    async def test_equal_requests(self):
        """Тестирование того, что одинаковые запросы для одного токена будут выполняться только один раз"""
        async with AsyncVkExecuteRequestPool() as pool:
            result = pool.add_call("groups.isMember", token1, {"user_id": 1, "group_id": 1})
            result2 = pool.add_call("groups.isMember", token1, {"user_id": 1, "group_id": 1})
            result3 = pool.add_call("groups.isMember", token1, {"user_id": 1, "group_id": 1})
            self.assertEqual(1, len(pool.pool[token1]))
        self.assertIs(result, result2)
        self.assertIs(result, result3)

    async def test_invalid_token(self):
        async with AsyncVkExecuteRequestPool() as pool:
            result = pool.add_call("groups.isMember", 'invalid_token', {"user_id": 1, "group_id": 1})
        self.assertEqual(5, result.error["error_code"])
        self.assertEqual("groups.isMember", result.error["method"])

    async def test_invalid_call(self):
        async with AsyncVkExecuteRequestPool() as pool:
            result = pool.add_call("groups.isMember", token1, {"user_id": -1, "group_id": 1})
        self.assertEqual(100, result.error['error_code'])

    async def test_invalid_token_type(self):
        """Вызов метода, который доступен только с токеном пользователя, с токеном группы"""
        async with AsyncVkExecuteRequestPool() as pool:
            result = pool.add_call("likes.isLiked", token1, {
                "user_id": 1,
                "owner_id": -1,
                "type": "post",
                "item_id": 396449,
            })
        self.assertIsNone(result.result)
        self.assertIsNotNone(result.error)
        self.assertEqual(27, result.error['error_code'])
        self.assertEqual('likes.isLiked', result.error['method'])
