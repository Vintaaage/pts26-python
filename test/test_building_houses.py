import json
import unittest
from typing import Any, Sequence

from power_grid.building_houses import BuildingHouses
from power_grid.interfaces import (
    InterfaceBuildingHousesTowns, InterfaceBuildingHousesPowerPlantMarket)
from power_grid.player_board_facade import PlayerBoardFacade
from power_grid.simple_types import PhaseStatus, PlayerColor, RequestError

RED = PlayerColor.RED
BLUE = PlayerColor.BLUE
GREEN = PlayerColor.GREEN


class TownsFake(InterfaceBuildingHousesTowns):
    result: int | RequestError
    max_houses: int
    calls: list[tuple[PlayerColor, list[str], int]]

    def __init__(self) -> None:
        self.result = 10
        self.max_houses = 0
        self.calls = []

    def buy_houses(self, player: PlayerColor, town_names: Sequence[str],
                   max_money: int) -> int | RequestError:
        self.calls.append((player, list(town_names), max_money))
        return self.result

    def get_max_number_of_houses(self) -> int:
        return self.max_houses


class PowerPlantMarketFake(InterfaceBuildingHousesPowerPlantMarket):
    removed_up_to: list[int]

    def __init__(self) -> None:
        self.removed_up_to = []

    def remove_power_plants_up_to(self, value: int) -> None:
        self.removed_up_to.append(value)


class TestBuildingHouses(unittest.TestCase):
    def setUp(self) -> None:
        self.towns = TownsFake()
        self.market = PowerPlantMarketFake()
        self.boards = {x: PlayerBoardFacade(x) for x in (RED, BLUE, GREEN)}
        self.phase = BuildingHouses(self.towns, self.market, self.boards)
        self.phase.start_phase([RED, BLUE, GREEN])

    def test_last_player_builds_first(self) -> None:
        self.assertEqual(self.phase.current_player(), GREEN)
        self.assertIsInstance(
            self.phase.buy_houses(RED, ["Berlin"]), RequestError)
        self.assertEqual(self.towns.calls, [])

    def test_building_pays_the_cost(self) -> None:
        result = self.phase.buy_houses(GREEN, ["Berlin", "Essen"])
        self.assertEqual(result, PhaseStatus.PHASE_CONTINUES)
        self.assertEqual(self.towns.calls, [(GREEN, ["Berlin", "Essen"], 50)])
        self.assertEqual(self.boards[GREEN].outstanding_money(), 40)
        self.assertEqual(self.phase.current_player(), BLUE)

    def test_building_nothing_is_allowed(self) -> None:
        self.assertEqual(self.phase.buy_houses(GREEN, []),
                         PhaseStatus.PHASE_CONTINUES)
        self.assertEqual(self.towns.calls, [])
        self.assertEqual(self.boards[GREEN].outstanding_money(), 50)
        self.assertEqual(self.phase.current_player(), BLUE)

    def test_error_from_towns_changes_nothing(self) -> None:
        self.towns.result = RequestError("Not enough money")
        result = self.phase.buy_houses(GREEN, ["Berlin"])
        self.assertIsInstance(result, RequestError)
        self.assertEqual(self.boards[GREEN].outstanding_money(), 50)
        self.assertEqual(self.phase.current_player(), GREEN)

    def test_phase_ends_after_the_first_player(self) -> None:
        self.phase.buy_houses(GREEN, [])
        self.phase.buy_houses(BLUE, [])
        self.assertEqual(self.market.removed_up_to, [])
        self.towns.max_houses = 7
        self.assertEqual(self.phase.buy_houses(RED, ["Berlin"]),
                         PhaseStatus.PHASE_ENDS)
        self.assertEqual(self.market.removed_up_to, [7])
        self.assertIsNone(self.phase.current_player())
        self.assertIsInstance(self.phase.buy_houses(RED, []), RequestError)

    def test_not_active_before_start(self) -> None:
        phase = BuildingHouses(self.towns, self.market, self.boards)
        self.assertIsInstance(phase.buy_houses(RED, []), RequestError)

    def test_state(self) -> None:
        state: Any = json.loads(self.phase.get_state())
        self.assertEqual(state["current_player"], "green")


if __name__ == "__main__":
    unittest.main()
