import os
from unittest import TestCase

from aiohttp.test_utils import setup_test_loop, teardown_test_loop

TEST_DIR = os.path.dirname(os.path.abspath(__file__))


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
