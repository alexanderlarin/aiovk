import asyncio
import unittest
import aio.testing
from src.authorisation import AuthSession
from src.exceptions import VkAuthError, VkTwoFactorCodeNeeded, VkCaptchaNeeded
from tests.test_auth_data import USER_LOGIN, USER_PASSWORD, APP_ID, USE_2FACTOR


class AuthSessionTestCase(unittest.TestCase):
    @aio.testing.run_until_complete
    def test_auth_with_empty_data(self):
        s = AuthSession(login='', password='', app_id='')
        with self.assertRaises(VkAuthError):
            yield from s.authorize()
        s.close()

    @aio.testing.run_until_complete
    def test_auth_with_app_id(self):
        s = AuthSession(login='', password='', app_id=APP_ID)
        with self.assertRaises(VkAuthError):
            yield from s.authorize()
        s.close()

    @aio.testing.run_until_complete
    def test_auth_with_invalid_password(self):
        s = AuthSession(login=USER_LOGIN, password='invalid', app_id=APP_ID)
        with self.assertRaises(VkAuthError):
            yield from s.authorize()
        s.close()

    @aio.testing.run_until_complete
    def test_auth_with_2factor(self):
        s = AuthSession(login=USER_LOGIN, password=USER_PASSWORD, app_id=APP_ID)
        with self.assertRaises(VkTwoFactorCodeNeeded):
            yield from s.authorize()
        s.close()

    @unittest.skipIf(not USE_2FACTOR, "your account don't use 2factor auth")
    @aio.testing.run_until_complete
    def test_auth_with_2factor(self):
        s = AuthSession(login=USER_LOGIN, password=USER_PASSWORD, app_id=APP_ID)
        with self.assertRaises(VkTwoFactorCodeNeeded):
            yield from s.authorize()
        s.close()

    @unittest.skipIf(USE_2FACTOR, "your account don't use 2factor auth")
    @aio.testing.run_until_complete
    def test_auth_process_captcha_without_2factor(self):
        s = AuthSession(login=USER_LOGIN, password=USER_PASSWORD, app_id=APP_ID)
        for i in range(10):
            with self.assertRaises(VkCaptchaNeeded):
                yield from s.authorize()
        s.close()
