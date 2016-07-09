import unittest
import aio.testing
import pyotp
from src.authorisation import AuthSession, SimpleAuthSession
from src.exceptions import VkAuthError, VkTwoFactorCodeNeeded, VkCaptchaNeeded
from tests.test_auth_data import USER_LOGIN, USER_PASSWORD, APP_ID, USE_2FACTOR, TWOFACTOR_CODE


class TestAuthSession(AuthSession):
    async def enter_confirmation_сode(self):
        totp = pyotp.TOTP(TWOFACTOR_CODE)
        return totp.now()


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

    @unittest.skipIf(not USE_2FACTOR, "your account use 2factor auth")
    @aio.testing.run_until_complete
    def test_auth_with_2factor(self):
        s = AuthSession(login=USER_LOGIN, password=USER_PASSWORD, app_id=APP_ID)
        with self.assertRaises(VkTwoFactorCodeNeeded):
            yield from s.authorize()
        s.close()

    @unittest.skipIf(USE_2FACTOR, "your account use 2factor auth")
    @aio.testing.run_until_complete
    def test_auth_without_2factor(self):
        s = AuthSession(login=USER_LOGIN, password=USER_PASSWORD, app_id=APP_ID)
        token = yield from s.authorize()
        s.close()
        self.assertIsNotNone(token)

    @aio.testing.run_until_complete
    def test_auth_one_text_scope(self):
        s = TestAuthSession(login=USER_LOGIN, password=USER_PASSWORD, app_id=APP_ID, scope='notify')
        token = yield from s.authorize()
        s.close()
        self.assertIsNotNone(token)

    @aio.testing.run_until_complete
    def test_auth_invalid_text_scope(self):
        s = TestAuthSession(login=USER_LOGIN, password=USER_PASSWORD, app_id=APP_ID, scope='a')
        token = yield from s.authorize()
        s.close()
        self.assertIsNotNone(token)

    @aio.testing.run_until_complete
    def test_auth_scopes_mask(self):
        # 3 == notify + friends
        s = TestAuthSession(login=USER_LOGIN, password=USER_PASSWORD, app_id=APP_ID, scope=3)
        token = yield from s.authorize()
        s.close()
        self.assertIsNotNone(token)

    @aio.testing.run_until_complete
    def test_auth_list_of_scopes(self):
        s = TestAuthSession(login=USER_LOGIN, password=USER_PASSWORD, app_id=APP_ID, scope=['notify', 'friends'])
        token = yield from s.authorize()
        s.close()
        self.assertIsNotNone(token)

    @unittest.skipIf(USE_2FACTOR, "your account use 2factor auth")
    @aio.testing.run_until_complete
    def test_auth_process_captcha_without_2factor(self):
        s = AuthSession(login=USER_LOGIN, password=USER_PASSWORD, app_id=APP_ID)
        for i in range(10):
            with self.assertRaises(VkCaptchaNeeded):
                yield from s.authorize()
        s.close()
