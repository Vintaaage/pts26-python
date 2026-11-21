import unittest
from dataclasses import FrozenInstanceError

from power_grid.simple_types import (
    PlayerColor, PowerPlant, PowerPlantNumber, RequestError, Resource)


class TestSimpleTypes(unittest.TestCase):
    def test_power_plant_number_equality(self) -> None:
        self.assertEqual(PowerPlantNumber(5), PowerPlantNumber(5))
        self.assertNotEqual(PowerPlantNumber(5), PowerPlantNumber(6))

    def test_power_plant_number_is_hashable(self) -> None:
        numbers = {PowerPlantNumber(5), PowerPlantNumber(5)}
        self.assertEqual(len(numbers), 1)

    def test_power_plant_is_immutable(self) -> None:
        plant = PowerPlant(PowerPlantNumber(5), (Resource.COAL,), 2, 1)
        with self.assertRaises(FrozenInstanceError):
            setattr(plant, "resource_amount", 3)

    def test_request_error_is_distinguishable(self) -> None:
        result: int | RequestError = RequestError("not enough money")
        self.assertTrue(isinstance(result, RequestError))

    def test_six_player_colors(self) -> None:
        self.assertEqual(len(PlayerColor), 6)
