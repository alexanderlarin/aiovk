import asyncio
from unittest.mock import Mock

import time
import math

from aiohttp.test_utils import unittest_run_loop

from aiovk.utils import TaskQueue, wait_free_slot
from tests.utils import AioTestCase


class TaskQueueTestCase(AioTestCase):
    @unittest_run_loop
    async def test_long_init(self):
        size = 1
        period = 1
        q = TaskQueue(size, period)
        self.assertEqual(q.qsize(), size)
        await asyncio.sleep(period + 1)
        self.assertEqual(q.qsize(), size)
        q.canel()

    @unittest_run_loop
    async def test_get_elem_and_pause(self):
        size = 1
        period = 1
        q = TaskQueue(size, period)
        self.assertEqual(q.qsize(), size)
        await q.get()
        self.assertEqual(q.qsize(), size - 1)
        await asyncio.sleep(period + 1)
        self.assertEqual(q.qsize(), size)
        q.canel()

    @unittest_run_loop
    async def test_get_all_plus_one_elem(self):
        size = 1
        period = 1
        q = TaskQueue(size, period)
        self.assertEqual(q.qsize(), size)
        await q.get()

        start = time.time()
        await q.get()
        stop = time.time()

        self.assertEqual(math.floor(stop - start), period)
        self.assertEqual(q.qsize(), 0)
        q.canel()


class WaitFreeSlotTestCase(AioTestCase):
    @unittest_run_loop
    async def test_simple_usage(self):
        @wait_free_slot
        async def foo(a):
            pass

        size = 1
        period = 1
        q = TaskQueue(size, period)
        obj = Mock()
        obj._queue = q

        await foo(obj)
        self.assertEqual(q.qsize(), size - 1)
        q.canel()

    @unittest_run_loop
    async def test_with_pause(self):
        @wait_free_slot
        async def foo(a):
            pass

        size = 1
        period = 1
        q = TaskQueue(size, period)
        obj = Mock()
        obj._queue = q
        await q.get()

        start = time.time()
        await foo(obj)
        stop = time.time()

        self.assertEqual(math.floor(stop - start), period)
        self.assertEqual(q.qsize(), 0)
        q.canel()
