import json
from typing import Mapping, Sequence
from power_grid.interfaces import InterfaceBuyingResourcesResourceMarket
from power_grid.player_board_facade import PlayerBoardFacade
from power_grid.simple_types import (
    PhaseStatus, PlayerColor, RequestError, Resource)


class BuyingResources:
    _market: InterfaceBuyingResourcesResourceMarket
    _boards: dict[PlayerColor, PlayerBoardFacade]
    _remaining: list[PlayerColor]

    def __init__(self, market: InterfaceBuyingResourcesResourceMarket,
                 boards: Mapping[PlayerColor, PlayerBoardFacade]):
        self._market = market
        self._boards = dict(boards)
        self._remaining = []

    def start_phase(self, player_order: Sequence[PlayerColor]) -> None:
        assert len(set(player_order)) == len(player_order)
        assert set(player_order) == set(self._boards)
        self._remaining = list(reversed(player_order))

    def current_player(self) -> PlayerColor | None:
        return self._remaining[0] if self._remaining else None

    def buy_resources(self, player: PlayerColor,
                      resources: Sequence[Resource]) -> PhaseStatus | RequestError:
        if player != self.current_player():
            return RequestError(f"It is not the turn of {player.name.lower()}")
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
        self._remaining.pop(0)
        if self._remaining:
            return PhaseStatus.PHASE_CONTINUES
        return PhaseStatus.PHASE_ENDS

    def get_state(self) -> str:
        current = self.current_player()
        return json.dumps({
            "phase": "buying_resources",
            "current_player": current.name.lower() if current else None
        })
