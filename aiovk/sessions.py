import json
import urllib.parse

from aiovk.drivers import HttpDriver
from aiovk.exceptions import VkAuthError, VkCaptchaNeeded, VkTwoFactorCodeNeeded, VkAPIError, CAPTCHA_IS_NEEDED, \
    AUTHORIZATION_FAILED
from aiovk.parser import AuthPageParser, TwoFactorCodePageParser, AccessPageParser


class TokenSession:
    API_VERSION = '5.52'
    REQUEST_URL = 'https://api.vk.com/method/'

    def __init__(self, access_token=None, timeout=10, driver=None):
        self.timeout = timeout
        self.access_token = access_token
        self.driver = HttpDriver(timeout) if driver is None else driver

    def close(self):
        self.driver.close()

    async def make_request(self, method_request, timeout=None):
        params = method_request._method_args
        return await self.send_api_request(method_request._method_name, params, timeout)

    async def send_api_request(self, method_name, params=None, timeout=None):
        if not timeout:
            timeout = self.timeout
        if not params:
            params = {}
        params['v'] = self.API_VERSION
        if self.access_token:
            params['access_token'] = self.access_token
        response = await self.driver.json(self.REQUEST_URL + method_name, params, timeout)
        error = response.get('error')
        if error:
            err_code = error.get('error_code')
            if err_code == CAPTCHA_IS_NEEDED:
                captcha_sid = error.get('captcha_sid')
                captcha_url = error.get('captcha_img')
                params['captcha_key'] = await self.enter_captcha(captcha_url, captcha_sid)
                params['captcha_sid'] = captcha_sid
                return await self.send_api_request(method_name, params, timeout)
            elif err_code == AUTHORIZATION_FAILED:
                await self.authorize()
                return await self.send_api_request(method_name, params, timeout)
            else:
                raise VkAPIError(error, self.REQUEST_URL + method_name)
        return response['response']

    async def authorize(self):
        raise VkAuthError('invalid_token', 'User authorization failed')

    async def enter_captcha(self, url, sid):
        """
        Override this method for processing captcha.
        :return captcha value
        """
        raise VkCaptchaNeeded(url, sid)


class ImplicitSession(TokenSession):
    """
    For client authorisation in js apps and standalone (desktop and mobile) apps
    See more in https://new.vk.com/dev/implicit_flow_user
    """
    AUTH_URL = 'https://oauth.vk.com/authorize'

    def __init__(self, login, password, app_id, scope=None, timeout=10, num_of_attempts=5, driver=None):
        super().__init__(access_token=None, timeout=timeout, driver=driver)
        self.login = login
        self.password = password
        self.app_id = app_id
        self.num_of_attempts = num_of_attempts
        if isinstance(scope, (str, int, type(None))):
            self.scope = scope
        elif isinstance(scope, list):
            self.scope = ",".join(scope)

    async def authorize(self):
        html = await self.get_auth_page()
        q = urllib.parse.urlparse('/authorize?email')
        for step in range(self.num_of_attempts):
            if q.path == '/authorize'and 'email' in q.query:  # invalid login or password  and 'email' in q.query
                url, html = await self.process_auth_form(html)
                q = urllib.parse.urlparse(url)
            if q.path == '/login':  # entering 2auth code
                url, html = await self.process_2auth_form(html)
                q = urllib.parse.urlparse(url)
            if q.path == '/authorize' and '__q_hash' in q.query:  # give rights for app
                url, html = await self.process_access_form(html)
                q = urllib.parse.urlparse(url)
            if q.path == '/blank.html':
                qs = dict(urllib.parse.parse_qsl(q.query))
                self.access_token = qs['access_token']
                return
        raise VkAuthError('Something went wrong', 'Exceeded the number of attempts to log in')

    async def get_auth_page(self):
        params = {'client_id': self.app_id,
                  'redirect_uri': 'https://oauth.vk.com/blank.html',
                  'display': 'mobile',
                  'response_type': 'token',
                  'v': self.API_VERSION
                  }

        if self.scope:
            params['scope'] = self.scope
        status, response = await self.driver.get_text(self.AUTH_URL, params)
        if status != 200:
            error_dict = json.loads(response)
            raise VkAuthError(error_dict['error'], error_dict['error_description'], self.AUTH_URL, params)
        return response

    async def process_auth_form(self, html):
        p = AuthPageParser()
        p.feed(html)
        p.close()
        form_data = dict(p.inputs)
        form_url = p.url
        form_data['email'] = self.login
        form_data['pass'] = self.password
        if p.message:
            raise VkAuthError('invalid_data', p.message, form_url, form_data)
        elif p.captcha_url:
            form_data['captcha_key'] = await self.enter_captcha(p.captcha_url, form_data['captcha_sid'])
        url, html = await self.driver.post_text(form_url, form_data)
        return url, html

    async def process_2auth_form(self, html):
        p = TwoFactorCodePageParser()
        p.feed(html)
        p.close()
        form_url = p.url
        form_data = dict(p.inputs)
        form_data['remember'] = 0
        if p.message:
            raise VkAuthError('invalid_data', p.message, form_url, form_data)
        form_data['code'] = await self.enter_confirmation_сode()
        url, html = await self.driver.post_text(form_url, form_data)
        return url, html

    async def process_access_form(self, html):
        p = AccessPageParser()
        p.feed(html)
        p.close()
        form_url = p.url
        form_data = dict(p.inputs)
        url, html = await self.driver.post_text(form_url, form_data)
        return url, html

    async def enter_confirmation_сode(self):
        """
        Override this method for processing confirmation 2uth code.
        :return confirmation code
        """
        raise VkTwoFactorCodeNeeded()


class SimpleImplicitSession(ImplicitSession):
    """
    Simple implementation of processing captcha and 2factor authorisation
    """

    async def enter_captcha(self, url, sid):
        bytes = await self.driver.get_bin(url, {})
        with open('captcha.jpg', 'wb') as f:
            f.write(bytes)
        return input("Enter captcha: ")

    async def enter_confirmation_сode(self):
        return input('Enter confirmation сode: ')


class AuthorizationCodeSession(TokenSession):
    CODE_URL = 'https://oauth.vk.com/access_token'

    def __init__(self, app_id, app_secret, redirect_uri, code, timeout=10, driver=None):
        super().__init__(access_token=None, timeout=timeout)
        self.code = code
        self.app_id = app_id
        self.app_secret = app_secret
        self.redirect_uri = redirect_uri
        self.driver = HttpDriver(timeout) if driver is None else driver

    async def authorize(self, code=None):
        code = await self.get_code(code)
        params = {
            'client_id': self.app_id,
            'client_secret': self.app_secret,
            'redirect_uri': self.redirect_uri,
            'code': code
        }
        response = await self.driver.json(self.CODE_URL, params, self.timeout)
        if 'error' in response:
            raise VkAuthError(response['error'], response['error_description'], self.CODE_URL, params)
        self.access_token = response['access_token']

    async def get_code(self, code=None):
        return code or self.code
