import json
import unittest
from typing import Any

from power_grid.resource_pool import ResourcePool
from power_grid.simple_types import Resource


class TestResourcePool(unittest.TestCase):
    def setUp(self) -> None:
        self.pool = ResourcePool(
            [Resource.COAL, Resource.COAL, Resource.OIL, Resource.URANIUM])

    def check(self, coal: int, oil: int, garbage: int, uranium: int) -> None:
        state: Any = json.loads(self.pool.to_string())
        self.assertEqual(state["coal"], coal)
        self.assertEqual(state["oil"], oil)
        self.assertEqual(state["garbage"], garbage)
        self.assertEqual(state["uranium"], uranium)

    def test_initial_state(self) -> None:
        self.check(2, 1, 0, 1)

    def test_empty_pool(self) -> None:
        empty = ResourcePool()
        state: Any = json.loads(empty.to_string())
        self.assertEqual(sum(state.values()), 0)

    def test_take_resources_enough(self) -> None:
        taken = self.pool.take_resources([Resource.COAL, Resource.OIL])
        self.assertEqual(taken, [Resource.COAL, Resource.OIL])
        self.check(1, 0, 0, 1)

    def test_take_resources_returns_only_available(self) -> None:
        taken = self.pool.take_resources(
            [Resource.COAL, Resource.COAL, Resource.COAL, Resource.GARBAGE])
        self.assertEqual(taken, [Resource.COAL, Resource.COAL])
        self.check(0, 1, 0, 1)

    def test_can_take_from_storage_space(self) -> None:
        self.assertTrue(self.pool.can_take_resources_from_storage_space(
            [Resource.COAL, Resource.COAL, Resource.URANIUM]))
        self.assertFalse(self.pool.can_take_resources_from_storage_space(
            [Resource.COAL, Resource.COAL, Resource.COAL]))
        self.assertFalse(self.pool.can_take_resources_from_storage_space(
            [Resource.GARBAGE]))

    def test_get_from_storage_space(self) -> None:
        self.pool.get_from_storage_space([Resource.COAL, Resource.URANIUM])
        self.check(1, 1, 0, 0)

    def test_get_from_storage_space_fails_when_missing(self) -> None:
        with self.assertRaises(AssertionError):
            self.pool.get_from_storage_space([Resource.GARBAGE])
        self.check(2, 1, 0, 1)

    def test_put_resources(self) -> None:
        self.pool.put_resources([Resource.GARBAGE, Resource.COAL])
        self.check(3, 1, 1, 1)


if __name__ == "__main__":
    unittest.main()
