import unittest

from power_grid.maximum_number_of_usable_power_plants import (
    MaximumNumberOfUsablePowerPlants, can_power_all)
from power_grid.simple_types import PowerPlant, PowerPlantNumber, Resource

COAL = Resource.COAL
OIL = Resource.OIL
URANIUM = Resource.URANIUM


def plant(number: int, accepted: tuple[Resource, ...], amount: int,
          cities: int) -> PowerPlant:
    return PowerPlant(PowerPlantNumber(number), accepted, amount, cities)


class TestCanPowerAll(unittest.TestCase):
    def test_no_plants(self) -> None:
        self.assertTrue(can_power_all([], []))
        self.assertTrue(can_power_all([COAL], []))

    def test_plant_without_resources_is_always_powered(self) -> None:
        self.assertTrue(can_power_all([], [plant(1, (), 0, 1)]))

    def test_not_enough_resources(self) -> None:
        self.assertFalse(can_power_all([COAL], [plant(3, (COAL,), 2, 1)]))

    def test_wrong_resource(self) -> None:
        self.assertFalse(can_power_all(
            [OIL, OIL], [plant(3, (COAL,), 2, 1)]))

    def test_two_plants_compete_for_the_same_resources(self) -> None:
        plants = [plant(3, (COAL,), 2, 1), plant(4, (COAL,), 2, 1)]
        self.assertFalse(can_power_all(3 * [COAL], plants))
        self.assertTrue(can_power_all(4 * [COAL], plants))

    def test_hybrid_takes_what_the_other_plant_leaves(self) -> None:
        plants = [plant(3, (COAL,), 1, 1), plant(4, (COAL, OIL), 2, 1)]
        self.assertTrue(can_power_all([COAL, OIL, OIL], plants))

    def test_resources_of_the_wrong_type_do_not_help(self) -> None:
        plants = [plant(3, (COAL,), 1, 1), plant(5, (OIL,), 1, 1)]
        self.assertFalse(can_power_all(3 * [COAL], plants))


class TestMaximumNumberOfUsablePowerPlants(unittest.TestCase):
    def setUp(self) -> None:
        self.maximum = MaximumNumberOfUsablePowerPlants()

    def test_nothing(self) -> None:
        self.assertEqual(self.maximum.number_of_suppliable_towns([], []), 0)

    def test_ecological_plant_needs_no_resources(self) -> None:
        self.assertEqual(self.maximum.number_of_suppliable_towns(
            [], [plant(13, (), 0, 1)]), 1)

    def test_single_plant(self) -> None:
        plants = [plant(5, (COAL,), 2, 3)]
        self.assertEqual(
            self.maximum.number_of_suppliable_towns(2 * [COAL], plants), 3)
        self.assertEqual(
            self.maximum.number_of_suppliable_towns([COAL], plants), 0)
        self.assertEqual(
            self.maximum.number_of_suppliable_towns(2 * [OIL], plants), 0)

    def test_unused_resources_do_not_matter(self) -> None:
        plants = [plant(5, (COAL,), 2, 3)]
        self.assertEqual(self.maximum.number_of_suppliable_towns(
            4 * [COAL] + [URANIUM], plants), 3)

    def test_chooses_the_better_plant_when_resources_are_short(self) -> None:
        plants = [plant(5, (COAL,), 2, 3), plant(6, (COAL,), 2, 5)]
        self.assertEqual(
            self.maximum.number_of_suppliable_towns(2 * [COAL], plants), 5)
        self.assertEqual(
            self.maximum.number_of_suppliable_towns(4 * [COAL], plants), 8)

    def test_ecological_plant_adds_to_the_others(self) -> None:
        plants = [plant(5, (COAL,), 2, 3), plant(13, (), 0, 1)]
        self.assertEqual(
            self.maximum.number_of_suppliable_towns(2 * [COAL], plants), 4)
        self.assertEqual(
            self.maximum.number_of_suppliable_towns([], plants), 1)

    def test_hybrid_plant_uses_any_mix(self) -> None:
        plants = [plant(2, (COAL, OIL), 2, 4)]
        self.assertEqual(
            self.maximum.number_of_suppliable_towns([COAL, OIL], plants), 4)

    def test_hybrid_and_dedicated_plant_share_resources(self) -> None:
        plants = [plant(3, (COAL,), 1, 2), plant(2, (COAL, OIL), 2, 4)]
        self.assertEqual(self.maximum.number_of_suppliable_towns(
            [COAL, OIL, OIL], plants), 6)
        self.assertEqual(self.maximum.number_of_suppliable_towns(
            [COAL, COAL, OIL], plants), 6)
        self.assertEqual(self.maximum.number_of_suppliable_towns(
            [COAL, OIL], plants), 4)


if __name__ == "__main__":
    unittest.main()
