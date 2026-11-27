import json
import unittest
from typing import Any

from power_grid.buying_resources import BuyingResources
from power_grid.interfaces import InterfaceBuyingResourcesResourceMarket
from power_grid.player_board_facade import PlayerBoardFacade
from power_grid.simple_types import (
    PhaseStatus, PlayerColor, PowerPlant, PowerPlantNumber, RequestError,
    Resource)

RED = PlayerColor.RED
BLUE = PlayerColor.BLUE
GREEN = PlayerColor.GREEN
COAL = Resource.COAL
URANIUM = Resource.URANIUM

COAL_PLANT = PowerPlant(PowerPlantNumber(5), (COAL,), 2, 3)


class MarketFake(InterfaceBuyingResourcesResourceMarket):
    unit_price: int
    unavailable: set[Resource]
    taken: list[list[Resource]]

    def __init__(self) -> None:
        self.unit_price = 3
        self.unavailable = set()
        self.taken = []

    def get_price(self, desired: list[Resource]) -> int | None:
        if any(x in self.unavailable for x in desired):
            return None
        return self.unit_price * len(desired)

    def take_resources(self, resources: list[Resource]) -> None:
        self.taken.append(resources)


class TestBuyingResources(unittest.TestCase):
    def setUp(self) -> None:
        self.market = MarketFake()
        self.boards = {x: PlayerBoardFacade(x) for x in (RED, BLUE, GREEN)}
        for board in self.boards.values():
            board.receive_power_plant(COAL_PLANT, 0)
        self.phase = BuyingResources(self.market, self.boards)
        self.phase.start_phase([RED, BLUE, GREEN])

    def test_last_player_buys_first(self) -> None:
        self.assertEqual(self.phase.current_player(), GREEN)
        self.assertIsInstance(
            self.phase.buy_resources(RED, [COAL]), RequestError)

    def test_buying_pays_stores_and_takes_from_market(self) -> None:
        result = self.phase.buy_resources(GREEN, [COAL, COAL])
        self.assertEqual(result, PhaseStatus.PHASE_CONTINUES)
        self.assertEqual(self.boards[GREEN].resources, [COAL, COAL])
        self.assertEqual(self.boards[GREEN].outstanding_money(), 44)
        self.assertEqual(self.market.taken, [[COAL, COAL]])
        self.assertEqual(self.phase.current_player(), BLUE)

    def test_buying_nothing_is_allowed(self) -> None:
        self.assertEqual(self.phase.buy_resources(GREEN, []),
                         PhaseStatus.PHASE_CONTINUES)
        self.assertEqual(self.boards[GREEN].outstanding_money(), 50)
        self.assertEqual(self.phase.current_player(), BLUE)

    def test_phase_ends_after_the_first_player(self) -> None:
        self.assertEqual(self.phase.buy_resources(GREEN, []),
                         PhaseStatus.PHASE_CONTINUES)
        self.assertEqual(self.phase.buy_resources(BLUE, []),
                         PhaseStatus.PHASE_CONTINUES)
        self.assertEqual(self.phase.buy_resources(RED, [COAL]),
                         PhaseStatus.PHASE_ENDS)
        self.assertIsNone(self.phase.current_player())
        self.assertIsInstance(
            self.phase.buy_resources(RED, []), RequestError)

    def test_not_enough_money(self) -> None:
        self.market.unit_price = 30
        result = self.phase.buy_resources(GREEN, [COAL, COAL])
        self.assertIsInstance(result, RequestError)
        self.assertEqual(self.boards[GREEN].resources, [])
        self.assertEqual(self.boards[GREEN].outstanding_money(), 50)
        self.assertEqual(self.market.taken, [])
        self.assertEqual(self.phase.current_player(), GREEN)

    def test_market_cannot_supply(self) -> None:
        self.market.unavailable = {COAL}
        self.assertIsInstance(
            self.phase.buy_resources(GREEN, [COAL]), RequestError)
        self.assertEqual(self.phase.current_player(), GREEN)

    def test_resources_do_not_fit_onto_power_plants(self) -> None:
        for result in (self.phase.buy_resources(GREEN, 5 * [COAL]),
                       self.phase.buy_resources(GREEN, [URANIUM])):
            self.assertIsInstance(result, RequestError)
        self.assertEqual(self.boards[GREEN].outstanding_money(), 50)
        self.assertEqual(self.market.taken, [])
        self.assertEqual(self.phase.current_player(), GREEN)

    def test_not_active_before_start(self) -> None:
        phase = BuyingResources(self.market, self.boards)
        self.assertIsInstance(phase.buy_resources(RED, []), RequestError)

    def test_state(self) -> None:
        state: Any = json.loads(self.phase.get_state())
        self.assertEqual(state["current_player"], "green")


if __name__ == "__main__":
    unittest.main()
