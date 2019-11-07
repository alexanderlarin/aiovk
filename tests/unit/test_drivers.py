import math
import time

from aiohttp.test_utils import unittest_run_loop

from aiovk.drivers import BaseDriver
from aiovk.mixins import LimitRateDriverMixin
from tests.utils import AioTestCase


class LimitRateBaseTestDriver(BaseDriver):
    async def post_json(self, *args, **kwargs):
        return 200, time.time()

    async def close(self):
        pass


class LimitRateTestDriver(LimitRateDriverMixin, LimitRateBaseTestDriver):
    period = 1
    requests_per_period = 1


class LimitRateDriverMixinTestCase(AioTestCase):
    period = 1
    requests_per_period = 1

    def get_driver(self):
        return LimitRateTestDriver()

    @unittest_run_loop
    async def test_json_fast(self):
        driver = self.get_driver()
        t0 = time.time()
        _, t1 = await driver.get_json()
        self.assertEqual(math.floor(t1 - t0), 0)
        await driver.close()

    @unittest_run_loop
    async def test_json_slow(self):
        driver = self.get_driver()
        _, t1 = await driver.get_json()
        _, t2 = await driver.get_json()
        self.assertEqual(math.floor(t2 - t1), self.period)
        await driver.close()
