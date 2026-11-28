import json
from typing import Mapping, Sequence
from power_grid.interfaces import InterfaceBuildingHousesTowns
from power_grid.player_board_facade import PlayerBoardFacade
from power_grid.reverse_order_phase import ReverseOrderPhase
from power_grid.simple_types import PhaseStatus, PlayerColor, RequestError


class BuildingHouses(ReverseOrderPhase):
    _towns: InterfaceBuildingHousesTowns
    _boards: dict[PlayerColor, PlayerBoardFacade]
    _houses_to_end_game: int

    def __init__(self, towns: InterfaceBuildingHousesTowns,
                 boards: Mapping[PlayerColor, PlayerBoardFacade],
                 houses_to_end_game: int):
        assert houses_to_end_game > 0
        super().__init__(boards.keys())
        self._towns = towns
        self._boards = dict(boards)
        self._houses_to_end_game = houses_to_end_game

    def buy_houses(self, player: PlayerColor,
                   town_names: Sequence[str]) -> PhaseStatus | RequestError:
        error = self._check_turn(player)
        if error is not None:
            return error
        board = self._boards[player]
        if town_names:
            cost = self._towns.buy_houses(
                player, town_names, board.outstanding_money())
            if isinstance(cost, RequestError):
                return cost
            board.spend_money(cost)
        status = self._finish_turn()
        if (status == PhaseStatus.PHASE_ENDS and
                self._towns.get_max_number_of_houses()
                >= self._houses_to_end_game):
            return PhaseStatus.GAME_ENDS
        return status

    def get_state(self) -> str:
        current = self.current_player()
        return json.dumps({
            "phase": "building_houses",
            "current_player": current.name.lower() if current else None,
        })
