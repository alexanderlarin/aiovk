import os
from unittest import TestCase

from aiohttp.test_utils import setup_test_loop, teardown_test_loop

TEST_DIR = os.path.dirname(os.path.abspath(__file__))


# class TestAuthSession(ImplicitSession):
#     async def enter_confirmation_code(self):
#         totp = pyotp.TOTP(TWOFACTOR_CODE)
#         return totp.now()
#
#     async def enter_captcha(self, url, sid):
#         bytes = await self.driver.get_bin(url, {})
#         file_path = os.path.join(TEST_DIR, "captcha.jpg")
#         with open(file_path, 'wb') as f:
#             f.write(bytes)
#         webbrowser.open("file://{}".format(file_path))
#         code = input("Enter captcha: ")
#         os.remove(file_path)
#         return code


class AioTestCase(TestCase):
    def setUp(self):
        self.loop = setup_test_loop()
        self.loop.run_until_complete(self.setUpAsync())

    async def setUpAsync(self):
        pass

    def tearDown(self):
        self.loop.run_until_complete(self.tearDownAsync())
        teardown_test_loop(self.loop)

    async def tearDownAsync(self):
        pass
