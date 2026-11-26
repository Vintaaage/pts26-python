import unittest

from power_grid.player_power_plants import PlayerPowerPlants
from power_grid.simple_types import (
    PowerPlant, PowerPlantNumber, RequestError, Resource)

COAL = Resource.COAL
OIL = Resource.OIL

COAL_PLANT = PowerPlant(PowerPlantNumber(5), (COAL,), 2, 3)
OIL_PLANT = PowerPlant(PowerPlantNumber(6), (OIL,), 1, 2)
ECO_PLANT = PowerPlant(PowerPlantNumber(13), (), 0, 1)
EXTRA_PLANT = PowerPlant(PowerPlantNumber(20), (COAL,), 3, 5)


class TestPlayerPowerPlants(unittest.TestCase):
    def test_no_power_plants(self) -> None:
        plants = PlayerPowerPlants()
        self.assertEqual(plants.best_power_plant(), PowerPlantNumber(0))
        self.assertEqual(plants.number_of_connectable_cities([COAL]), 0)
        self.assertFalse(plants.can_store_resources([COAL]))

    def test_receive_power_plants_up_to_the_limit(self) -> None:
        plants = PlayerPowerPlants()
        self.assertTrue(plants.receive_power_plant(COAL_PLANT))
        self.assertTrue(plants.receive_power_plant(OIL_PLANT))
        self.assertTrue(plants.receive_power_plant(ECO_PLANT))
        self.assertFalse(plants.receive_power_plant(EXTRA_PLANT))
        self.assertEqual(len(plants.power_plants), 3)

    def test_best_power_plant(self) -> None:
        plants = PlayerPowerPlants([COAL_PLANT, ECO_PLANT, OIL_PLANT])
        self.assertEqual(plants.best_power_plant(), PowerPlantNumber(13))

    def test_remove_power_plant(self) -> None:
        plants = PlayerPowerPlants([COAL_PLANT, OIL_PLANT])
        self.assertIsNone(plants.remove_power_plant(PowerPlantNumber(5), [OIL]))
        self.assertEqual(plants.power_plants, [OIL_PLANT])

    def test_remove_unknown_power_plant(self) -> None:
        plants = PlayerPowerPlants([COAL_PLANT])
        self.assertIsInstance(
            plants.remove_power_plant(PowerPlantNumber(6), []), RequestError)

    def test_remove_fails_if_resources_do_not_fit_any_more(self) -> None:
        plants = PlayerPowerPlants([COAL_PLANT, OIL_PLANT])
        error = plants.remove_power_plant(PowerPlantNumber(5), [COAL])
        self.assertIsInstance(error, RequestError)
        self.assertEqual(plants.power_plants, [COAL_PLANT, OIL_PLANT])

    def test_connectable_cities_and_storage(self) -> None:
        plants = PlayerPowerPlants([COAL_PLANT, OIL_PLANT])
        self.assertEqual(
            plants.number_of_connectable_cities([COAL, COAL, OIL]), 5)
        self.assertTrue(plants.can_store_resources(4 * [COAL] + 2 * [OIL]))
        self.assertFalse(plants.can_store_resources(5 * [COAL]))

    def test_use_power_plant(self) -> None:
        plants = PlayerPowerPlants([COAL_PLANT, OIL_PLANT])
        self.assertEqual(plants.use_power_plant(
            [PowerPlantNumber(5), PowerPlantNumber(6)], [COAL, COAL, OIL]), 5)

    def test_use_power_plant_not_owned(self) -> None:
        plants = PlayerPowerPlants([COAL_PLANT])
        self.assertIsInstance(plants.use_power_plant(
            [PowerPlantNumber(6)], [OIL]), RequestError)

    def test_use_power_plant_with_wrong_resources(self) -> None:
        plants = PlayerPowerPlants([COAL_PLANT])
        self.assertIsInstance(plants.use_power_plant(
            [PowerPlantNumber(5)], [COAL]), RequestError)

    def test_use_the_same_power_plant_twice(self) -> None:
        plants = PlayerPowerPlants([COAL_PLANT])
        self.assertIsInstance(plants.use_power_plant(
            [PowerPlantNumber(5), PowerPlantNumber(5)], 4 * [COAL]),
            RequestError)


if __name__ == "__main__":
    unittest.main()
    