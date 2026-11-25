import unittest

from power_grid.simple_types import (
    PowerPlant, PowerPlantNumber, RequestError, Resource)
from power_grid.use_power_plants import UsePowerPlants

COAL = Resource.COAL
OIL = Resource.OIL


def plant(number: int, accepted: tuple[Resource, ...], amount: int,
          cities: int) -> PowerPlant:
    return PowerPlant(PowerPlantNumber(number), accepted, amount, cities)


class TestUsePowerPlants(unittest.TestCase):
    def setUp(self) -> None:
        self.use = UsePowerPlants()

    def test_nothing_used(self) -> None:
        self.assertEqual(self.use.number_of_suppliable_towns([], []), 0)

    def test_single_plant(self) -> None:
        self.assertEqual(self.use.number_of_suppliable_towns(
            2 * [COAL], [plant(5, (COAL,), 2, 3)]), 3)

    def test_several_plants_add_up(self) -> None:
        plants = [plant(5, (COAL,), 2, 3), plant(6, (OIL,), 1, 2)]
        self.assertEqual(self.use.number_of_suppliable_towns(
            [COAL, COAL, OIL], plants), 5)

    def test_hybrid_plant_accepts_a_mix(self) -> None:
        self.assertEqual(self.use.number_of_suppliable_towns(
            [COAL, OIL], [plant(2, (COAL, OIL), 2, 4)]), 4)

    def test_ecological_plant_needs_no_resources(self) -> None:
        self.assertEqual(self.use.number_of_suppliable_towns(
            [], [plant(13, (), 0, 1)]), 1)

    def test_too_few_resources(self) -> None:
        self.assertIsInstance(self.use.number_of_suppliable_towns(
            [COAL], [plant(5, (COAL,), 2, 3)]), RequestError)

    def test_too_many_resources(self) -> None:
        self.assertIsInstance(self.use.number_of_suppliable_towns(
            3 * [COAL], [plant(5, (COAL,), 2, 3)]), RequestError)

    def test_resources_without_plants(self) -> None:
        self.assertIsInstance(
            self.use.number_of_suppliable_towns([COAL], []), RequestError)

    def test_wrong_resource_type(self) -> None:
        self.assertIsInstance(self.use.number_of_suppliable_towns(
            2 * [OIL], [plant(5, (COAL,), 2, 3)]), RequestError)

    def test_right_count_but_wrong_distribution(self) -> None:
        plants = [plant(5, (COAL,), 1, 3), plant(6, (OIL,), 1, 2)]
        self.assertIsInstance(self.use.number_of_suppliable_towns(
            2 * [COAL], plants), RequestError)

    def test_same_plant_twice(self) -> None:
        same = plant(5, (COAL,), 1, 3)
        self.assertIsInstance(self.use.number_of_suppliable_towns(
            2 * [COAL], [same, same]), RequestError)


if __name__ == "__main__":
    unittest.main()
