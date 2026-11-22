import unittest

from power_grid.simple_types import PowerPlant, PowerPlantNumber, Resource
from power_grid.store_resources import StoreResources

COAL = Resource.COAL
OIL = Resource.OIL
GARBAGE = Resource.GARBAGE
URANIUM = Resource.URANIUM


def plant(number: int, accepted: tuple[Resource, ...],
          amount: int) -> PowerPlant:
    return PowerPlant(PowerPlantNumber(number), accepted, amount, 1)


class TestStoreResources(unittest.TestCase):
    def setUp(self) -> None:
        self.store = StoreResources()

    def test_nothing_to_store(self) -> None:
        self.assertTrue(self.store.can_store_resources([], []))
        self.assertTrue(self.store.can_store_resources(
            [], [plant(3, (OIL,), 2)]))

    def test_no_power_plants_cannot_store_anything(self) -> None:
        self.assertFalse(self.store.can_store_resources([COAL], []))

    def test_plant_stores_twice_its_amount(self) -> None:
        plants = [plant(4, (COAL,), 2)]
        self.assertTrue(self.store.can_store_resources(4 * [COAL], plants))
        self.assertFalse(self.store.can_store_resources(5 * [COAL], plants))

    def test_plant_accepts_only_its_resource(self) -> None:
        plants = [plant(4, (COAL,), 2)]
        self.assertFalse(self.store.can_store_resources([OIL], plants))
        self.assertFalse(self.store.can_store_resources([COAL, URANIUM], plants))

    def test_plants_without_resources_store_nothing(self) -> None:
        plants = [plant(1, (), 0)]
        self.assertFalse(self.store.can_store_resources([COAL], plants))

    def test_capacities_of_several_plants_add_up(self) -> None:
        plants = [plant(4, (COAL,), 1), plant(5, (COAL,), 2)]
        self.assertTrue(self.store.can_store_resources(6 * [COAL], plants))
        self.assertFalse(self.store.can_store_resources(7 * [COAL], plants))

    def test_different_resources_for_different_plants(self) -> None:
        plants = [plant(3, (OIL,), 1), plant(8, (URANIUM,), 1)]
        self.assertTrue(self.store.can_store_resources(
            [OIL, OIL, URANIUM], plants))
        self.assertFalse(self.store.can_store_resources(
            [OIL, URANIUM, URANIUM, URANIUM], plants))

    def test_hybrid_plant_stores_any_mix(self) -> None:
        plants = [plant(2, (COAL, OIL), 2)]
        self.assertTrue(self.store.can_store_resources(
            [COAL, COAL, OIL, OIL], plants))
        self.assertTrue(self.store.can_store_resources(4 * [OIL], plants))
        self.assertFalse(self.store.can_store_resources(5 * [OIL], plants))
        self.assertFalse(self.store.can_store_resources([GARBAGE], plants))

    def test_hybrid_plant_takes_overflow_of_dedicated_plant(self) -> None:
        plants = [plant(4, (COAL,), 1), plant(2, (COAL, OIL), 2)]
        self.assertTrue(self.store.can_store_resources(6 * [COAL], plants))
        self.assertTrue(self.store.can_store_resources(
            5 * [COAL] + [OIL], plants))
        self.assertFalse(self.store.can_store_resources(
            6 * [COAL] + [OIL], plants))

    def test_assignment_must_not_use_hybrid_space_twice(self) -> None:
        plants = [plant(3, (OIL,), 1), plant(2, (COAL, OIL), 1)]
        self.assertTrue(self.store.can_store_resources(
            [COAL] + 3 * [OIL], plants))
        self.assertFalse(self.store.can_store_resources(
            2 * [COAL] + 3 * [OIL], plants))


if __name__ == "__main__":
    unittest.main()
