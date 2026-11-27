import json
from typing import Mapping, Sequence
from power_grid.interfaces import (
    InterfaceBuildingHousesTowns, InterfaceBuildingHousesPowerPlantMarket)
from power_grid.player_board_facade import PlayerBoardFacade
from power_grid.reverse_order_phase import ReverseOrderPhase
from power_grid.simple_types import PhaseStatus, PlayerColor, RequestError


class BuildingHouses(ReverseOrderPhase):
    _towns: InterfaceBuildingHousesTowns
    _power_plant_market: InterfaceBuildingHousesPowerPlantMarket
    _boards: dict[PlayerColor, PlayerBoardFacade]

    def __init__(self, towns: InterfaceBuildingHousesTowns,
                 power_plant_market: InterfaceBuildingHousesPowerPlantMarket,
                 boards: Mapping[PlayerColor, PlayerBoardFacade]):
        super().__init__(boards.keys())
        self._towns = towns
        self._power_plant_market = power_plant_market
        self._boards = dict(boards)

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
        if status == PhaseStatus.PHASE_ENDS:
            self._power_plant_market.remove_power_plants_up_to(
                self._towns.get_max_number_of_houses())
        return status

    def get_state(self) -> str:
        current = self.current_player()
        return json.dumps({
            "phase": "building_houses",
            "current_player": current.name.lower() if current else None,
        })
