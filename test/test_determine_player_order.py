import unittest

from power_grid.determine_player_order import DeterminePlayerOrder
from power_grid.interfaces import (
    InterfaceDeterminePlayerOrderTowns,
    InterfaceDeterminePlayerOrderPlayerBoard)
from power_grid.simple_types import PlayerColor, PowerPlantNumber

RED = PlayerColor.RED
BLUE = PlayerColor.BLUE
GREEN = PlayerColor.GREEN


class TownsFake(InterfaceDeterminePlayerOrderTowns):
    houses: dict[PlayerColor, int]

    def __init__(self) -> None:
        self.houses = {}

    def get_number_of_houses(self, player: PlayerColor) -> int:
        return self.houses[player]


class PlayerBoardFake(InterfaceDeterminePlayerOrderPlayerBoard):
    best_plant: int
    money: int
    connectable_cities: int

    def __init__(self) -> None:
        self.best_plant = 0
        self.money = 0
        self.connectable_cities = 0

    def best_power_plant_number(self) -> PowerPlantNumber:
        return PowerPlantNumber(self.best_plant)

    def outstanding_money(self) -> int:
        return self.money

    def number_of_connectable_cities(self) -> int:
        return self.connectable_cities


class TestDeterminePlayerOrder(unittest.TestCase):
    def setUp(self) -> None:
        self.towns = TownsFake()
        self.boards = {RED: PlayerBoardFake(), BLUE: PlayerBoardFake(),
                       GREEN: PlayerBoardFake()}
        self.towns.houses = {RED: 0, BLUE: 0, GREEN: 0}
        self.order = DeterminePlayerOrder(
            [RED, BLUE, GREEN], self.towns, self.boards)

    def test_initial_order_is_kept(self) -> None:
        self.assertEqual(self.order.get_order(), [RED, BLUE, GREEN])

    def test_reorder_by_number_of_houses(self) -> None:
        self.towns.houses = {RED: 2, BLUE: 5, GREEN: 3}
        self.assertEqual(self.order.reorder(), [BLUE, GREEN, RED])
        self.assertEqual(self.order.get_order(), [BLUE, GREEN, RED])

    def test_houses_tie_is_broken_by_best_power_plant(self) -> None:
        self.towns.houses = {RED: 3, BLUE: 3, GREEN: 3}
        self.boards[RED].best_plant = 13
        self.boards[BLUE].best_plant = 25
        self.boards[GREEN].best_plant = 4
        self.assertEqual(self.order.reorder(), [BLUE, RED, GREEN])

    def test_more_houses_beat_better_power_plant(self) -> None:
        self.towns.houses = {RED: 4, BLUE: 3, GREEN: 3}
        self.boards[BLUE].best_plant = 50
        self.assertEqual(self.order.reorder(), [RED, BLUE, GREEN])

    def test_complete_tie_keeps_current_order(self) -> None:
        self.assertEqual(self.order.reorder(), [RED, BLUE, GREEN])
        self.towns.houses = {RED: 1, BLUE: 2, GREEN: 2}
        self.assertEqual(self.order.reorder(), [BLUE, GREEN, RED])
        self.towns.houses = {RED: 1, BLUE: 1, GREEN: 1}
        self.assertEqual(self.order.reorder(), [BLUE, GREEN, RED])

    def test_result_most_powered_cities_wins(self) -> None:
        self.towns.houses = {RED: 10, BLUE: 10, GREEN: 10}
        self.boards[RED].connectable_cities = 6
        self.boards[BLUE].connectable_cities = 9
        self.boards[GREEN].connectable_cities = 7
        self.assertEqual(self.order.game_result(), [BLUE, GREEN, RED])

    def test_result_powered_cities_are_capped_by_houses(self) -> None:
        self.towns.houses = {RED: 5, BLUE: 7, GREEN: 0}
        self.boards[RED].connectable_cities = 20
        self.boards[BLUE].connectable_cities = 6
        self.boards[GREEN].connectable_cities = 0
        self.assertEqual(self.order.game_result(), [BLUE, RED, GREEN])

    def test_result_tie_is_broken_by_money(self) -> None:
        self.towns.houses = {RED: 10, BLUE: 10, GREEN: 10}
        for board in self.boards.values():
            board.connectable_cities = 8
        self.boards[RED].money = 30
        self.boards[BLUE].money = 50
        self.boards[GREEN].money = 40
        self.assertEqual(self.order.game_result(), [BLUE, GREEN, RED])

    def test_result_money_tie_is_broken_by_houses(self) -> None:
        self.towns.houses = {RED: 9, BLUE: 12, GREEN: 10}
        for board in self.boards.values():
            board.connectable_cities = 8
            board.money = 10
        self.assertEqual(self.order.game_result(), [BLUE, GREEN, RED])

    def test_unknown_player_set_is_rejected(self) -> None:
        with self.assertRaises(AssertionError):
            DeterminePlayerOrder([RED, BLUE], self.towns, self.boards)


if __name__ == "__main__":
    unittest.main()
