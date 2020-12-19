from urllib.parse import urlencode


CAPTCHA_IS_NEEDED = 14
AUTHORIZATION_FAILED = 5  # invalid access token


class VkException(Exception):
    pass


class VkAuthError(VkException):
    def __init__(self, error, description, url='', params=''):
        self.error = error
        self.description = description
        self.url = "{}?{}".format(url, urlencode(params))

    def __str__(self):
        return self.description


class VkCaptchaNeeded(VkException):
    def __init__(self, url, sid):
        self.url = url
        self.sid = sid

    def __str__(self):
        return "You must enter the captcha"


class VkTwoFactorCodeNeeded(VkException):
    def __str__(self):
        return "In order to confirm that you are the owner of this page " \
               "please enter the code provided by the code generating app."


class VkAPIError(VkException):
    def __init__(self, error, url):
        self.error_code = error.get('error_code')
        self.error_msg = error.get('error_msg')
        self.params = {param['key']: param['value'] for param in error.get('request_params', [])}
        self.url = url


class VkLongPollError(VkException):
    def __init__(self, error, description, url='', params=''):
        self.error = error
        self.description = description
        self.url = "{}?{}".format(url, urlencode(params))

    def __str__(self):
        return self.description
