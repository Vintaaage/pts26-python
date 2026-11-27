import json
import unittest
from typing import Any

from power_grid.interfaces import InterfaceDeterminePlayerOrderPlayerBoard
from power_grid.player_board_facade import PlayerBoardFacade
from power_grid.simple_types import (
    PlayerColor, PowerPlant, PowerPlantNumber, RequestError, Resource)

COAL = Resource.COAL
OIL = Resource.OIL

COAL_PLANT = PowerPlant(PowerPlantNumber(5), (COAL,), 2, 3)
OIL_PLANT = PowerPlant(PowerPlantNumber(6), (OIL,), 1, 2)
ECO_PLANT = PowerPlant(PowerPlantNumber(13), (), 0, 1)
EXTRA_PLANT = PowerPlant(PowerPlantNumber(20), (COAL,), 3, 5)


class TestPlayerBoardFacade(unittest.TestCase):
    def setUp(self) -> None:
        self.board = PlayerBoardFacade(PlayerColor.RED)

    def test_initial_state(self) -> None:
        self.assertEqual(self.board.color, PlayerColor.RED)
        self.assertEqual(self.board.outstanding_money(), 50)
        self.assertEqual(self.board.best_power_plant_number(),
                         PowerPlantNumber(0))
        self.assertEqual(self.board.number_of_connectable_cities(), 0)
        self.assertIsInstance(
            self.board, InterfaceDeterminePlayerOrderPlayerBoard)

    def test_money(self) -> None:
        self.assertTrue(self.board.has_enough_money(50))
        self.assertFalse(self.board.has_enough_money(51))
        self.board.spend_money(20)
        self.assertEqual(self.board.outstanding_money(), 30)
        self.board.receive_money(0)
        self.assertEqual(self.board.outstanding_money(), 40)

    def test_receive_power_plant_charges_the_price(self) -> None:
        self.assertTrue(self.board.receive_power_plant(COAL_PLANT, 12))
        self.assertEqual(self.board.outstanding_money(), 38)
        self.assertEqual(self.board.power_plants, [COAL_PLANT])
        self.assertEqual(self.board.best_power_plant_number(),
                         PowerPlantNumber(5))

    def test_receive_power_plant_above_the_limit_is_free(self) -> None:
        for plant in (COAL_PLANT, OIL_PLANT, ECO_PLANT):
            self.assertTrue(self.board.receive_power_plant(plant, 1))
        self.assertFalse(self.board.receive_power_plant(EXTRA_PLANT, 10))
        self.assertEqual(self.board.outstanding_money(), 47)
        self.assertEqual(len(self.board.power_plants), 3)

    def test_receive_power_plant_needs_enough_money(self) -> None:
        with self.assertRaises(AssertionError):
            self.board.receive_power_plant(COAL_PLANT, 51)

    def test_buy_resources(self) -> None:
        self.board.receive_power_plant(COAL_PLANT, 0)
        self.assertIsNone(self.board.buy_resources([COAL, COAL]))
        self.assertEqual(self.board.resources, [COAL, COAL])
        self.assertIsInstance(
            self.board.buy_resources(3 * [COAL]), RequestError)
        self.assertEqual(self.board.resources, [COAL, COAL])

    def test_connectable_cities(self) -> None:
        self.board.receive_power_plant(COAL_PLANT, 0)
        self.board.receive_power_plant(ECO_PLANT, 0)
        self.assertEqual(self.board.number_of_connectable_cities(), 1)
        self.board.buy_resources([COAL, COAL])
        self.assertEqual(self.board.number_of_connectable_cities(), 4)

    def test_use_power_plants(self) -> None:
        self.board.receive_power_plant(COAL_PLANT, 0)
        self.board.buy_resources(3 * [COAL])
        result = self.board.use_power_plants([PowerPlantNumber(5)], 2 * [COAL])
        self.assertEqual(result, 3)
        self.assertEqual(self.board.resources, [COAL])

    def test_use_power_plants_with_error(self) -> None:
        self.board.receive_power_plant(COAL_PLANT, 0)
        result = self.board.use_power_plants([PowerPlantNumber(5)], 2 * [COAL])
        self.assertIsInstance(result, RequestError)

    def test_remove_power_plant(self) -> None:
        self.board.receive_power_plant(COAL_PLANT, 0)
        self.board.receive_power_plant(OIL_PLANT, 0)
        self.board.buy_resources([COAL, OIL])
        self.assertIsInstance(
            self.board.remove_power_plant(PowerPlantNumber(5), []),
            RequestError)
        self.assertIsNone(
            self.board.remove_power_plant(PowerPlantNumber(5), [COAL]))
        self.assertEqual(self.board.power_plants, [OIL_PLANT])
        self.assertEqual(self.board.resources, [OIL])

    def test_state(self) -> None:
        self.board.receive_power_plant(COAL_PLANT, 10)
        self.board.buy_resources([COAL])
        state: Any = json.loads(self.board.state())
        self.assertEqual(state, {
            "color": "red", "money": 40, "power_plants": [5],
            "resources": ["coal"]})


if __name__ == "__main__":
    unittest.main()
