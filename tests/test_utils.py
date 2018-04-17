import asyncio
import unittest
from unittest.mock import Mock

import aio.testing
import time
import math

from aiovk.utils import TaskQueue, wait_free_slot


class TaskQueueTestCase(unittest.TestCase):
    @aio.testing.run_until_complete
    def test_long_init(self):
        size = 1
        period = 1
        q = TaskQueue(size, period)
        self.assertEqual(q.qsize(), size)
        yield from asyncio.sleep(period + 1)
        self.assertEqual(q.qsize(), size)
        q.canel()

    @aio.testing.run_until_complete
    def test_get_elem_and_pause(self):
        size = 1
        period = 1
        q = TaskQueue(size, period)
        self.assertEqual(q.qsize(), size)
        yield from q.get()
        self.assertEqual(q.qsize(), size - 1)
        yield from asyncio.sleep(period + 1)
        self.assertEqual(q.qsize(), size)
        q.canel()

    @aio.testing.run_until_complete
    def test_get_all_plus_one_elem(self):
        size = 1
        period = 1
        q = TaskQueue(size, period)
        self.assertEqual(q.qsize(), size)
        yield from q.get()

        start = time.time()
        yield from q.get()
        stop = time.time()

        self.assertEqual(math.floor(stop - start), period)
        self.assertEqual(q.qsize(), 0)
        q.canel()


class WaitFreeSlotTestCase(unittest.TestCase):
    @aio.testing.run_until_complete
    def test_simple_usage(self):
        @wait_free_slot
        async def foo(a):
            pass

        size = 1
        period = 1
        q = TaskQueue(size, period)
        obj = Mock()
        obj._queue = q

        yield from foo(obj)
        self.assertEqual(q.qsize(), size - 1)
        q.canel()

    @aio.testing.run_until_complete
    def test_with_pause(self):
        @wait_free_slot
        async def foo(a):
            pass

        size = 1
        period = 1
        q = TaskQueue(size, period)
        obj = Mock()
        obj._queue = q
        yield from q.get()

        start = time.time()
        yield from foo(obj)
        stop = time.time()

        self.assertEqual(math.floor(stop - start), period)
        self.assertEqual(q.qsize(), 0)
        q.canel()
