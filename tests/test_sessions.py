import unittest
from http.server import HTTPServer
from threading import Thread

import aio.testing
import aiohttp

from aiovk import ImplicitSession, TokenSession, AuthorizationCodeSession
from aiovk.drivers import CustomClientResponse
from aiovk.exceptions import VkAuthError, VkTwoFactorCodeNeeded, VkCaptchaNeeded
from tests.auth_data import USER_LOGIN, USER_PASSWORD, APP_ID, TWOFACTOR_CODE, REDIRECT_URI, APP_SECRET, \
    REDIRECT_URI_PORT
from tests.helpers import MockServerRequestHandler, TestAuthSession


class TokenSessionTestCase(unittest.TestCase):
    @classmethod
    @aio.testing.run_until_complete
    def setUpClass(cls):
        s = TestAuthSession(login=USER_LOGIN, password=USER_PASSWORD, app_id=APP_ID)
        yield from s.authorize()
        s.close()
        cls._token = s.access_token

    @aio.testing.run_until_complete
    def test_auth_with_empty_token(self):
        s = TokenSession()
        with self.assertRaises(VkAuthError):
            yield from s.authorize()
        s.close()

    @aio.testing.run_until_complete
    def test_auth_with_token(self):
        s = TokenSession(self._token)
        with self.assertRaises(VkAuthError):
            yield from s.authorize()
        s.close()

    @aio.testing.run_until_complete
    def test_auth_token_free_request_without_token(self):
        s = TokenSession()
        result = yield from s.send_api_request('users.get', {'user_ids': 1})
        s.close()
        self.assertListEqual(result, [{'id': 1, 'last_name': 'Дуров', 'first_name': 'Павел'}])

    @aio.testing.run_until_complete
    def test_auth_token_nonfree_request_without_token(self):
        s = TokenSession()
        with self.assertRaises(VkAuthError):
            yield from s.send_api_request('messages.get')
        s.close()


class ImplicitSessionTestCase(unittest.TestCase):
    @aio.testing.run_until_complete
    def test_auth_with_empty_data(self):
        s = ImplicitSession(login='', password='', app_id='')
        with self.assertRaises(VkAuthError):
            yield from s.authorize()
        s.close()

    @aio.testing.run_until_complete
    def test_auth_with_app_id(self):
        s = ImplicitSession(login='', password='', app_id=APP_ID)
        with self.assertRaises(VkAuthError):
            yield from s.authorize()
        s.close()

    @aio.testing.run_until_complete
    def test_auth_with_invalid_password(self):
        s = ImplicitSession(login=USER_LOGIN, password='invalid', app_id=APP_ID)
        with self.assertRaises(VkAuthError):
            yield from s.authorize()
        s.close()

    @unittest.skipIf(not TWOFACTOR_CODE, "your account use 2factor auth")
    @aio.testing.run_until_complete
    def test_auth_with_2factor(self):
        s = ImplicitSession(login=USER_LOGIN, password=USER_PASSWORD, app_id=APP_ID)
        with self.assertRaises(VkTwoFactorCodeNeeded):
            yield from s.authorize()
        s.close()

    @unittest.skipIf(TWOFACTOR_CODE, "your account use 2factor auth")
    @aio.testing.run_until_complete
    def test_auth_without_2factor(self):
        s = ImplicitSession(login=USER_LOGIN, password=USER_PASSWORD, app_id=APP_ID)
        yield from s.authorize()
        s.close()
        self.assertIsNotNone(s.access_token)

    @aio.testing.run_until_complete
    def test_auth_without_scope(self):
        s = TestAuthSession(login=USER_LOGIN, password=USER_PASSWORD, app_id=APP_ID)
        yield from s.authorize()
        s.close()
        self.assertIsNotNone(s.access_token)

    @aio.testing.run_until_complete
    def test_auth_one_text_scope(self):
        s = TestAuthSession(login=USER_LOGIN, password=USER_PASSWORD, app_id=APP_ID, scope='notify')
        yield from s.authorize()
        s.close()
        self.assertIsNotNone(s.access_token)

    @aio.testing.run_until_complete
    def test_auth_invalid_text_scope(self):
        s = TestAuthSession(login=USER_LOGIN, password=USER_PASSWORD, app_id=APP_ID, scope='a')
        yield from s.authorize()
        s.close()
        self.assertIsNotNone(s.access_token)

    @aio.testing.run_until_complete
    def test_auth_scopes_mask(self):
        # 3 == notify + friends
        s = TestAuthSession(login=USER_LOGIN, password=USER_PASSWORD, app_id=APP_ID, scope=3)
        yield from s.authorize()
        s.close()
        self.assertIsNotNone(s.access_token)

    @aio.testing.run_until_complete
    def test_auth_list_of_scopes(self):
        s = TestAuthSession(login=USER_LOGIN, password=USER_PASSWORD, app_id=APP_ID, scope=['notify', 'friends'])
        yield from s.authorize()
        s.close()
        self.assertIsNotNone(s.access_token)

    @aio.testing.run_until_complete
    def test_auth_string_of_scopes(self):
        s = TestAuthSession(login=USER_LOGIN, password=USER_PASSWORD, app_id=APP_ID, scope='notify,friends')
        yield from s.authorize()
        s.close()
        self.assertIsNotNone(s.access_token)

    @unittest.skipIf(TWOFACTOR_CODE, "your account use 2factor auth")
    @aio.testing.run_until_complete
    def test_auth_process_captcha_without_2factor(self):
        s = ImplicitSession(login=USER_LOGIN, password=USER_PASSWORD, app_id=APP_ID)
        for i in range(10):
            with self.assertRaises(VkCaptchaNeeded):
                yield from s.authorize()
        s.close()


@unittest.skipIf(not REDIRECT_URI, 'you do not give me this value')
class AuthorizationCodeSessionTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Configure mock server.
        cls.mock_server_port = REDIRECT_URI_PORT
        cls.mock_server = HTTPServer(('localhost', cls.mock_server_port), MockServerRequestHandler)

        # Start running mock server in a separate thread.
        # Daemon threads automatically shut down when the main process exits.
        cls.mock_server_thread = Thread(target=cls.mock_server.serve_forever)
        cls.mock_server_thread.setDaemon(True)
        cls.mock_server_thread.start()

        cls.json_url = 'http://localhost:{port}/'.format(port=cls.mock_server_port)

    @aio.testing.run_until_complete
    def test_auth_with_empty_data(self):
        s = AuthorizationCodeSession('', '', '', '')
        with self.assertRaises(VkAuthError):
            yield from s.authorize()
        s.close()

    @aio.testing.run_until_complete
    def test_auth_with_expired_code(self):
        s = AuthorizationCodeSession(APP_ID, APP_SECRET, REDIRECT_URI, '')
        with self.assertRaises(VkAuthError):
            yield from s.authorize()
        s.close()

    @aio.testing.run_until_complete
    def test_auth_with_valid_data(self):
        s = TestAuthSession(login=USER_LOGIN, password=USER_PASSWORD, app_id=APP_ID)
        s.driver.session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False),
                                                 response_class=CustomClientResponse)
        yield from s.authorize()
        params = {'client_id': APP_ID, 'display': 'page', 'redirect_uri': REDIRECT_URI, 'response_type': 'code'}
        with aiohttp.Timeout(10):
            response = yield from s.driver.session.get("https://oauth.vk.com/authorize",
                                                       params=params, allow_redirects=True)
        s.close()
        code = response.url.query.get('code')
        self.assertIsNotNone(code)

        s = AuthorizationCodeSession(APP_ID, APP_SECRET, REDIRECT_URI, code)
        yield from s.authorize()
        s.close()
        self.assertIsNotNone(s.access_token)
