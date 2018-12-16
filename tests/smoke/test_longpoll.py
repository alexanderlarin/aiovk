import os
import ssl
from http.server import HTTPServer
from threading import Thread

from aiohttp.test_utils import unittest_run_loop

from aiovk import API
from aiovk.longpoll import LongPoll
# from tests.auth_data import USER_LOGIN, USER_PASSWORD, APP_ID
from tests.utils import AioTestCase, TEST_DIR
from tests.smoke.utils import disable_cert_verification, VKRequestHandler, TestTokenSession, TestInternalAuthSession, \
    get_free_port


class LongPollRealTestCase(AioTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Configure mock server.
        cls.mock_server_port = get_free_port()
        cls.mock_server = HTTPServer(('localhost', cls.mock_server_port), VKRequestHandler)
        cls.mock_server.socket = ssl.wrap_socket(cls.mock_server.socket, server_side=True,
                                                 certfile=os.path.join(TEST_DIR, 'certs', 'cert.pem'),
                                                 keyfile=os.path.join(TEST_DIR, 'certs', 'key.pem'))

        # Start running mock server in a separate thread.
        # Daemon threads automatically shut down when the main process exits.
        cls.mock_server_thread = Thread(target=cls.mock_server.serve_forever)
        cls.mock_server_thread.setDaemon(True)
        cls.mock_server_thread.start()
        cls.base_url = 'localhost:{port}'.format(port=cls.mock_server_port)

    @disable_cert_verification
    @unittest_run_loop
    async def test_wait_valid_with_token_session(self):
        s = TestInternalAuthSession(login='login', password='pass', app_id='123', scope='messages')
        s.BASE_URL = self.base_url
        await s.authorize()
        await s.close()

        t = TestTokenSession(s.access_token, timeout=1000)
        t.BASE_URL = self.base_url
        api = API(t)
        lp = LongPoll(api, mode=2, wait=2)

        response = await lp.wait()
        await t.close()
        self.assertTrue('ts' in response)
        self.assertTrue('updates' in response)

    @disable_cert_verification
    @unittest_run_loop
    async def test_wait_valid_with_session_authorised(self):
        s = TestInternalAuthSession(login='login', password='pass', app_id='123', scope='messages')
        s.BASE_URL = self.base_url
        await s.authorize()

        lp = LongPoll(s, mode=2, wait=2)

        response = await lp.wait()
        await s.close()
        self.assertTrue('ts' in response)
        self.assertTrue('updates' in response)

    @disable_cert_verification
    @unittest_run_loop
    async def test_wait_valid_with_session_auto_auth(self):
        s = TestInternalAuthSession(login='login', password='pass', app_id='123', scope='messages')
        s.BASE_URL = self.base_url

        api = API(s)
        lp = LongPoll(api, mode=2, wait=2)

        response = await lp.wait()
        await s.close()
        self.assertTrue('ts' in response)
        self.assertTrue('updates' in response)
