from typing import Mapping, Sequence
from power_grid.interfaces import (
    InterfaceDeterminePlayerOrderTowns,
    InterfaceDeterminePlayerOrderPlayerBoard)
from power_grid.simple_types import PlayerColor


class DeterminePlayerOrder:
    _order: list[PlayerColor]
    _towns: InterfaceDeterminePlayerOrderTowns
    _boards: dict[PlayerColor, InterfaceDeterminePlayerOrderPlayerBoard]

    def __init__(
            self, initial_order: Sequence[PlayerColor],
            towns: InterfaceDeterminePlayerOrderTowns,
            boards: Mapping[PlayerColor,
                            InterfaceDeterminePlayerOrderPlayerBoard]):
        assert len(set(initial_order)) == len(initial_order)
        assert set(boards) == set(initial_order)
        self._order = list(initial_order)
        self._towns = towns
        self._boards = dict(boards)

    def get_order(self) -> list[PlayerColor]:
        return list(self._order)

    def reorder(self) -> list[PlayerColor]:
        self._order = sorted(self._order, key=self._reorder_key)
        return self.get_order()

    def game_result(self) -> list[PlayerColor]:
        return sorted(self._order, key=self._result_key)

    def _reorder_key(self, player: PlayerColor) -> tuple[int, int]:
        houses = self._towns.get_number_of_houses(player)
        best_plant = self._boards[player].best_power_plant_number().number
        return (-houses, -best_plant)

    def _result_key(self, player: PlayerColor) -> tuple[int, int, int]:
        houses = self._towns.get_number_of_houses(player)
        board = self._boards[player]
        powered = min(houses, board.number_of_connectable_cities())
        return (-powered, -board.outstanding_money(), -houses)
