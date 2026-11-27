import json
from typing import Mapping, Sequence
from power_grid.interfaces import InterfaceBuyingResourcesResourceMarket
from power_grid.player_board_facade import PlayerBoardFacade
from power_grid.reverse_order_phase import ReverseOrderPhase
from power_grid.simple_types import (
    PhaseStatus, PlayerColor, RequestError, Resource)


class BuyingResources(ReverseOrderPhase):
    _market: InterfaceBuyingResourcesResourceMarket
    _boards: dict[PlayerColor, PlayerBoardFacade]

    def __init__(self, market: InterfaceBuyingResourcesResourceMarket,
                 boards: Mapping[PlayerColor, PlayerBoardFacade]):
        super().__init__(boards.keys())
        self._market = market
        self._boards = dict(boards)

    def buy_resources(self, player: PlayerColor,
                      resources: Sequence[Resource]) -> PhaseStatus | RequestError:
        """Every player buys exactly once, possibly nothing (empty list)."""
        error = self._check_turn(player)
        if error is not None:
            return error
        wanted = list(resources)
        price = self._market.get_price(wanted)
        if price is None:
            return RequestError("The market cannot supply these resources")
        board = self._boards[player]
        if not board.has_enough_money(price):
            return RequestError("Not enough money for these resources")
        error = board.buy_resources(wanted)
        if error is not None:
            return error
        self._market.take_resources(wanted)
        board.spend_money(price)
        return self._finish_turn()

    def get_state(self) -> str:
        current = self.current_player()
        return json.dumps({
            "phase": "buying_resources",
            "current_player": current.name.lower() if current else None,
        })
