import json
from abc import ABC, abstractmethod

from yarl import URL

from aiovk.drivers import HttpDriver
from aiovk.exceptions import VkAuthError, VkCaptchaNeeded, VkTwoFactorCodeNeeded, VkAPIError, CAPTCHA_IS_NEEDED, \
    AUTHORIZATION_FAILED
from aiovk.parser import AuthPageParser, TwoFactorCodePageParser, AccessPageParser


class BaseSession(ABC):
    """Interface for all types of sessions"""

    @abstractmethod
    async def __aenter__(self):
        """Make avaliable usage of "async with" context manager"""

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Closes session after usage of context manager with Session"""
        await self.close()

    async def close(self) -> None:
        """Perform the actions associated with the completion of the current session"""

    @abstractmethod
    async def send_api_request(self, method_name: str, params: dict = None, timeout: int = None) -> dict:
        """Method that use API instance for sending request to vk server

        :param method_name: any value from the left column of the methods table from `https://vk.com/dev/methods`
        :param params: dict of params that available for current method.
                       For example see `Parameters` block from: `https://vk.com/dev/account.getInfo`
        :param timeout: timeout for response from the server
        :return: dict that contain data from `Result` block. Example see here: `https://vk.com/dev/account.getInfo`
        """


class TokenSession(BaseSession):
    """Implements simple session that ues existed token for work"""

    API_VERSION = '5.74'
    REQUEST_URL = 'https://api.vk.com/method/'

    def __init__(self, access_token: str = None, timeout: int = 10, driver=None):
        """
        :param access_token: see `User Token` block from `https://vk.com/dev/access_token`
        :param timeout: default time out for any request in current session
        :param driver: TODO add description
        """
        self.timeout = timeout
        self.access_token = access_token
        self.driver = HttpDriver(timeout) if driver is None else driver

    async def __aenter__(self) -> BaseSession:
        """Make available usage of `async with` context manager"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return await self.driver.close()

    async def send_api_request(self, method_name: str, params: dict = None, timeout: int = None) -> dict:
        # Prepare request
        if not timeout:
            timeout = self.timeout
        if not params:
            params = {}
        if self.access_token:
            params['access_token'] = self.access_token
        params['v'] = self.API_VERSION

        # Send request
        response = await self.driver.json(self.REQUEST_URL + method_name, params, timeout)

        # Process response
        # Checking the section with errors
        error = response.get('error')
        if error:
            err_code = error.get('error_code')
            if err_code == CAPTCHA_IS_NEEDED:
                # Collect information about Captcha
                captcha_sid = error.get('captcha_sid')
                captcha_url = error.get('captcha_img')
                params['captcha_key'] = await self.enter_captcha(captcha_url, captcha_sid)
                params['captcha_sid'] = captcha_sid
                # Send request again
                # Provide one attempt to repeat the request
                return await self.send_api_request(method_name, params, timeout)
            elif err_code == AUTHORIZATION_FAILED:
                await self.authorize()
                # Send request again
                # Provide one attempt to repeat the request
                return await self.send_api_request(method_name, params, timeout)
            else:
                # Other errors is not related with security
                raise VkAPIError(error, self.REQUEST_URL + method_name)
        # Must return only useful data
        return response['response']

    async def authorize(self) -> None:
        """Getting a new token from server"""
        # For `TokenSession` we have not credentials for getting new token
        raise VkAuthError('invalid_token', 'User authorization failed')

    async def enter_captcha(self, url: str, sid: str) -> str:
        """
        Override this method for processing captcha.

        :param url: link to captcha image
        :param sid: captcha id. I do not know why pass here but may be useful
        :return captcha value
        """
        raise VkCaptchaNeeded(url, sid)


class ImplicitSession(TokenSession):
    """
    For client authorization in js apps and standalone (desktop and mobile) apps
    See more in https://new.vk.com/dev/implicit_flow_user
    """
    AUTH_URL = 'https://oauth.vk.com/authorize'

    def __init__(self, login: str, password: str, app_id: int, scope: str or int or list = None,
                 timeout: int = 10, num_of_attempts: int = 5, driver=None):
        """
        :param login: user login
        :param password: user password
        :param app_id: application id. More details in `Application registration` block in `https://vk.com/dev/first_guide`
        :param scope: access rights. See `Access rights` block in `https://vk.com/dev/first_guide`
        :param timeout: default time out for any request in current session
        :param num_of_attempts: number of authorization attempts
        :param driver: TODO add description
        """
        super().__init__(access_token=None, timeout=timeout, driver=driver)
        self.login = login
        self.password = password
        self.app_id = app_id
        self.num_of_attempts = num_of_attempts
        if isinstance(scope, (str, int, type(None))):
            self.scope = scope
        elif isinstance(scope, list):
            self.scope = ",".join(scope)

    async def authorize(self) -> None:
        """Getting a new token from server"""
        html = await self._get_auth_page()
        url = URL('/authorize?email')
        for step in range(self.num_of_attempts):
            if url.path == '/authorize' and 'email' in url.query:
                # Invalid login or password  and 'email' in q.query
                url, html = await self._process_auth_form(html)
            if url.path == '/login' and url.query.get('act', '') == 'authcheck':
                # Entering 2auth code
                url, html = await self._process_2auth_form(html)
            if url.path == '/login' and url.query.get('act', '') == 'authcheck_code':
                # Need captcha
                url, html = await self._process_auth_form(html)
            if url.path == '/authorize' and '__q_hash' in url.query:
                # Give rights for app
                url, html = await self._process_access_form(html)
            if url.path == '/blank.html':
                # Success
                self.access_token = url.query['access_token']
                return
        raise VkAuthError('Something went wrong', 'Exceeded the number of attempts to log in')

    async def _get_auth_page(self) -> str:
        """
        Get authorization mobile page without js
        :return: html page
        """
        # Prepare request
        params = {
            'client_id': self.app_id,
            'redirect_uri': 'https://oauth.vk.com/blank.html',
            'display': 'mobile',
            'response_type': 'token',
            'v': self.API_VERSION
        }
        if self.scope:
            params['scope'] = self.scope

        # Send request
        status, response = await self.driver.get_text(self.AUTH_URL, params)

        # Process response
        if status != 200:
            error_dict = json.loads(response)
            raise VkAuthError(error_dict['error'], error_dict['error_description'], self.AUTH_URL, params)
        return response

    async def _process_auth_form(self, html: str) -> (str, str):
        """
        Parsing data from authorization page and filling the form and submitting the form

        :param html: html page
        :return: url and  html from redirected page
        """
        # Parse page
        p = AuthPageParser()
        p.feed(html)
        p.close()

        # Get data from hidden inputs
        form_data = dict(p.inputs)
        form_url = p.url
        form_data['email'] = self.login
        form_data['pass'] = self.password
        if p.message:
            # Show form errors
            raise VkAuthError('invalid_data', p.message, form_url, form_data)
        elif p.captcha_url:
            form_data['captcha_key'] = await self.enter_captcha(
                "https://m.vk.com{}".format(p.captcha_url),
                form_data['captcha_sid']
            )
            form_url = "https://m.vk.com{}".format(form_url)

        # Send request
        url, html = await self.driver.post_text(form_url, form_data)
        return url, html

    async def _process_2auth_form(self, html: str) -> (str, str):
        """
        Parsing two-factor authorization page and filling the code

        :param html: html page
        :return: url and  html from redirected page
        """
        # Parse page
        p = TwoFactorCodePageParser()
        p.feed(html)
        p.close()

        # Prepare request data
        form_url = p.url
        form_data = dict(p.inputs)
        form_data['remember'] = 0
        if p.message:
            raise VkAuthError('invalid_data', p.message, form_url, form_data)
        form_data['code'] = await self.enter_confirmation_code()

        # Send request
        url, html = await self.driver.post_text(form_url, form_data)
        return url, html

    async def _process_access_form(self, html: str) -> (str, str):
        """
        Parsing page with access rights

        :param html: html page
        :return: url and  html from redirected page
        """
        # Parse page
        p = AccessPageParser()
        p.feed(html)
        p.close()

        form_url = p.url
        form_data = dict(p.inputs)

        # Send request
        url, html = await self.driver.post_text(form_url, form_data)
        return url, html

    async def enter_confirmation_code(self) -> str:
        """
        Override this method for processing confirmation 2uth code.
        :return confirmation code
        """
        raise VkTwoFactorCodeNeeded()


class AuthorizationCodeSession(TokenSession):
    """
    For client authorization in js apps and standalone (desktop and mobile) apps
    See more in https://new.vk.com/dev/implicit_flow_user
    """
    CODE_URL = 'https://oauth.vk.com/access_token'

    def __init__(self, app_id: int, app_secret: str, redirect_uri: str, code: str, timeout: int = 10, driver=None):
        """
        :param app_id: application id. More details in `Application registration` block in `https://vk.com/dev/first_guide`
        :param app_secret: application secure key. See https://vk.com/editapp?id={app_id}&section=options
        :param redirect_uri: Authorized redirect URI.
        :param code: See `https://vk.com/dev/authcode_flow_user`
        :param timeout:default time out for any request in current session
        :param driver: TODO add description
        """
        super().__init__(access_token=None, timeout=timeout, driver=driver)
        self.code = code
        self.app_id = app_id
        self.app_secret = app_secret
        self.redirect_uri = redirect_uri

    async def authorize(self, code: str=None) -> None:
        """Getting a new token from server"""
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

    async def get_code(self, code: str=None) -> str:
        """Get temporary code from external sources"""
        return code or self.code
