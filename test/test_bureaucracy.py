import json
import unittest
from typing import Any, Sequence

from power_grid.bureaucracy import Bureaucracy
from power_grid.interfaces import (
    InterfaceBureaucracyTowns, InterfaceBureaucracyResourcePool,
    InterfaceBureaucracyResourceMarket, InterfaceBureaucracyPowerPlantMarket)
from power_grid.player_board_facade import PlayerBoardFacade
from power_grid.simple_types import (
    PhaseStatus, PlayerColor, PowerPlant, PowerPlantNumber, RequestError,
    Resource)

RED = PlayerColor.RED
BLUE = PlayerColor.BLUE
COAL = Resource.COAL
PLANT_5 = PowerPlantNumber(5)
COAL_PLANT = PowerPlant(PLANT_5, (COAL,), 2, 3)


class TownsFake(InterfaceBureaucracyTowns):
    houses: dict[PlayerColor, int]

    def __init__(self) -> None:
        self.houses = {RED: 5, BLUE: 5}

    def get_number_of_houses(self, player: PlayerColor) -> int:
        return self.houses[player]

    def get_max_number_of_houses(self) -> int:
        return max(self.houses.values())


class PoolFake(InterfaceBureaucracyResourcePool):
    received: list[Resource]

    def __init__(self) -> None:
        self.received = []

    def put_resources(self, resources: Sequence[Resource]) -> None:
        self.received += resources


class ResourceMarketFake(InterfaceBureaucracyResourceMarket):
    refills: int

    def __init__(self) -> None:
        self.refills = 0

    def refill(self) -> None:
        self.refills += 1


class PowerPlantMarketFake(InterfaceBureaucracyPowerPlantMarket):
    prepared: int

    def __init__(self) -> None:
        self.prepared = 0

    def prepare_next_turn(self) -> None:
        self.prepared += 1


class TestBureaucracy(unittest.TestCase):
    def setUp(self) -> None:
        self.towns = TownsFake()
        self.pool = PoolFake()
        self.resource_market = ResourceMarketFake()
        self.plant_market = PowerPlantMarketFake()
        self.boards = {x: PlayerBoardFacade(x) for x in (RED, BLUE)}
        self.boards[RED].receive_power_plant(COAL_PLANT, 0)
        self.boards[RED].buy_resources(3 * [COAL])
        self.bureaucracy = Bureaucracy(
            self.boards, self.towns, self.pool, self.resource_market,
            self.plant_market, 17)
        self.bureaucracy.start_phase([RED, BLUE])

    def test_using_a_power_plant_pays_income_and_burns_resources(self) -> None:
        result = self.bureaucracy.use_power_plants(RED, [PLANT_5], 2 * [COAL])
        self.assertEqual(result, PhaseStatus.PHASE_CONTINUES)
        self.assertEqual(self.boards[RED].outstanding_money(), 50 + 44)
        self.assertEqual(self.boards[RED].resources, [COAL])
        self.assertEqual(self.pool.received, 2 * [COAL])

    def test_income_is_limited_by_the_number_of_houses(self) -> None:
        self.towns.houses[RED] = 2
        self.bureaucracy.use_power_plants(RED, [PLANT_5], 2 * [COAL])
        self.assertEqual(self.boards[RED].outstanding_money(), 50 + 33)

    def test_using_nothing_still_pays_the_minimum(self) -> None:
        result = self.bureaucracy.use_power_plants(BLUE, [], [])
        self.assertEqual(result, PhaseStatus.PHASE_CONTINUES)
        self.assertEqual(self.boards[BLUE].outstanding_money(), 60)
        self.assertEqual(self.pool.received, [])

    def test_invalid_choice_changes_nothing(self) -> None:
        result = self.bureaucracy.use_power_plants(RED, [PLANT_5], [COAL])
        self.assertIsInstance(result, RequestError)
        self.assertEqual(self.boards[RED].outstanding_money(), 50)
        self.assertEqual(self.boards[RED].resources, 3 * [COAL])
        self.assertEqual(self.pool.received, [])
        self.assertEqual(self.bureaucracy.use_power_plants(
            RED, [PLANT_5], 2 * [COAL]), PhaseStatus.PHASE_CONTINUES)

    def test_players_may_act_in_any_order_but_only_once(self) -> None:
        self.bureaucracy.use_power_plants(BLUE, [], [])
        self.assertIsInstance(
            self.bureaucracy.use_power_plants(BLUE, [], []), RequestError)
        self.assertEqual(self.bureaucracy.use_power_plants(RED, [], []),
                         PhaseStatus.PHASE_ENDS)

    def test_phase_ends_with_refill_and_next_turn_preparation(self) -> None:
        self.bureaucracy.use_power_plants(RED, [], [])
        self.assertEqual(self.resource_market.refills, 0)
        self.assertEqual(self.bureaucracy.use_power_plants(BLUE, [], []),
                         PhaseStatus.PHASE_ENDS)
        self.assertEqual(self.resource_market.refills, 1)
        self.assertEqual(self.plant_market.prepared, 1)

    def test_game_ends_when_a_player_has_enough_houses(self) -> None:
        self.towns.houses[BLUE] = 17
        self.bureaucracy.use_power_plants(RED, [], [])
        self.assertEqual(self.bureaucracy.use_power_plants(BLUE, [], []),
                         PhaseStatus.GAME_ENDS)
        self.assertEqual(self.resource_market.refills, 0)
        self.assertEqual(self.plant_market.prepared, 0)

    def test_not_active_before_start(self) -> None:
        bureaucracy = Bureaucracy(
            self.boards, self.towns, self.pool, self.resource_market,
            self.plant_market, 17)
        self.assertIsInstance(
            bureaucracy.use_power_plants(RED, [], []), RequestError)

    def test_state(self) -> None:
        self.bureaucracy.use_power_plants(RED, [], [])
        state: Any = json.loads(self.bureaucracy.get_state())
        self.assertEqual(state["waiting_for"], ["blue"])


if __name__ == "__main__":
    unittest.main()
