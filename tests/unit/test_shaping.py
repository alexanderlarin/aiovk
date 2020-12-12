import asyncio
import time

import pytest

from aiovk.drivers import BaseDriver
from aiovk.mixins import LimitRateDriverMixin

pytestmark = pytest.mark.asyncio


class LimitRateBaseTestDriver(BaseDriver):
    async def post_json(self, *args, **kwargs):
        return 200, time.time()

    async def close(self):
        pass


class LimitRateTestDriver(LimitRateDriverMixin, LimitRateBaseTestDriver):
    pass


@pytest.mark.parametrize(
    'period, requests_per_period, rps, lower, upper', [
        (1, 1, 1, 0, 0.01),
        (1, 1, 2, 1, 1.01),
        (1, 1, 2, 1, 1.01),
        (2, 2, 2, 0, 0.01),
        (2, 1, 2, 0, 2.01),
    ]
)
async def test_request_shaper_mixin(period, requests_per_period, rps, lower, upper):
    driver = LimitRateTestDriver(period=period, requests_per_period=requests_per_period)
    t0 = time.time()
    data = await asyncio.gather(*(driver.post_json() for _ in range(rps)))
    await driver.close()
    max_time = max(v[1] for v in data)
    assert lower < max_time - t0 < upper
