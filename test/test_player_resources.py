import unittest

from power_grid.player_power_plants import PlayerPowerPlants
from power_grid.player_resources import PlayerResources
from power_grid.simple_types import (
    PowerPlant, PowerPlantNumber, RequestError, Resource)

COAL = Resource.COAL
OIL = Resource.OIL

COAL_PLANT = PowerPlant(PowerPlantNumber(5), (COAL,), 2, 3)
OIL_PLANT = PowerPlant(PowerPlantNumber(6), (OIL,), 1, 2)


class TestPlayerResources(unittest.TestCase):
    def setUp(self) -> None:
        self.plants = PlayerPowerPlants([COAL_PLANT, OIL_PLANT])
        self.player = PlayerResources(self.plants)

    def test_starts_empty(self) -> None:
        self.assertEqual(self.player.resources, [])

    def test_buy_resources(self) -> None:
        self.assertIsNone(self.player.buy_resources([COAL, OIL]))
        self.assertIsNone(self.player.buy_resources([COAL]))
        self.assertCountEqual(self.player.resources, [COAL, COAL, OIL])

    def test_buy_more_than_fits(self) -> None:
        self.assertIsNone(self.player.buy_resources(4 * [COAL]))
        self.assertIsInstance(self.player.buy_resources([COAL]), RequestError)
        self.assertEqual(self.player.resources, 4 * [COAL])

    def test_buy_resource_without_matching_plant(self) -> None:
        self.assertIsInstance(
            self.player.buy_resources([Resource.URANIUM]), RequestError)
        self.assertEqual(self.player.resources, [])

    def test_remove_power_plant_discarding_resources(self) -> None:
        self.player.buy_resources([COAL, COAL, OIL])
        self.assertIsNone(
            self.player.remove_power_plant(PowerPlantNumber(5), [COAL, COAL]))
        self.assertEqual(self.player.resources, [OIL])
        self.assertEqual(self.plants.power_plants, [OIL_PLANT])

    def test_remove_power_plant_without_discarding_enough(self) -> None:
        self.player.buy_resources([COAL, OIL])
        error = self.player.remove_power_plant(PowerPlantNumber(5), [])
        self.assertIsInstance(error, RequestError)
        self.assertCountEqual(self.player.resources, [COAL, OIL])
        self.assertEqual(len(self.plants.power_plants), 2)

    def test_remove_power_plant_discarding_missing_resources(self) -> None:
        self.player.buy_resources([COAL])
        error = self.player.remove_power_plant(PowerPlantNumber(5), [OIL])
        self.assertIsInstance(error, RequestError)
        self.assertEqual(self.player.resources, [COAL])

    def test_number_of_connectable_cities(self) -> None:
        self.assertEqual(self.player.number_of_connectable_cities(), 0)
        self.player.buy_resources([COAL, COAL, OIL])
        self.assertEqual(self.player.number_of_connectable_cities(), 5)

    def test_use_power_plant_burns_resources(self) -> None:
        self.player.buy_resources([COAL, COAL, COAL, OIL])
        result = self.player.use_power_plant([PowerPlantNumber(5)], [COAL, COAL])
        self.assertEqual(result, 3)
        self.assertCountEqual(self.player.resources, [COAL, OIL])

    def test_use_power_plant_with_resources_not_owned(self) -> None:
        self.player.buy_resources([COAL])
        result = self.player.use_power_plant([PowerPlantNumber(5)], [COAL, COAL])
        self.assertIsInstance(result, RequestError)
        self.assertEqual(self.player.resources, [COAL])

    def test_use_power_plant_with_invalid_choice(self) -> None:
        self.player.buy_resources([COAL, COAL])
        result = self.player.use_power_plant([PowerPlantNumber(6)], [COAL])
        self.assertIsInstance(result, RequestError)
        self.assertEqual(self.player.resources, [COAL, COAL])


if __name__ == "__main__":
    unittest.main()
