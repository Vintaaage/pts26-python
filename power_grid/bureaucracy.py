import json
from typing import Mapping, Sequence
from power_grid.interfaces import (
    InterfaceBureaucracyTowns, InterfaceBureaucracyResourcePool,
    InterfaceBureaucracyResourceMarket, InterfaceBureaucracyPowerPlantMarket)
from power_grid.player_board_facade import PlayerBoardFacade
from power_grid.simple_types import (
    PhaseStatus, PlayerColor, PowerPlantNumber, RequestError, Resource)


class Bureaucracy:
    _boards: dict[PlayerColor, PlayerBoardFacade]
    _towns: InterfaceBureaucracyTowns
    _resource_pool: InterfaceBureaucracyResourcePool
    _resource_market: InterfaceBureaucracyResourceMarket
    _power_plant_market: InterfaceBureaucracyPowerPlantMarket
    _houses_to_end_game: int
    _pending: list[PlayerColor]

    def __init__( # pylint: disable=too-many-arguments,too-many-positional-arguments
            self, boards: Mapping[PlayerColor, PlayerBoardFacade],
            towns: InterfaceBureaucracyTowns,
            resource_pool: InterfaceBureaucracyResourcePool,
            resource_market: InterfaceBureaucracyResourceMarket,
            power_plant_market: InterfaceBureaucracyPowerPlantMarket,
            houses_to_end_game: int):
        assert houses_to_end_game > 0
        self._boards = dict(boards)
        self._towns = towns
        self._resource_pool = resource_pool
        self._resource_market = resource_market
        self._power_plant_market = power_plant_market
        self._houses_to_end_game = houses_to_end_game
        self._pending = []

    def start_phase(self, player_order: Sequence[PlayerColor]) -> None:
        assert len(set(player_order)) == len(player_order)
        assert set(player_order) == set(self._boards)
        self._pending = list(player_order)

    def use_power_plants(
            self, player: PlayerColor, ppns: Sequence[PowerPlantNumber],
            resources_to_burn: Sequence[Resource]) -> PhaseStatus | RequestError:
        if player not in self._pending:
            return RequestError(
                f"{player.name.lower()} cannot use power plants now")
        board = self._boards[player]
        supplied = board.use_power_plants(ppns, resources_to_burn)
        if isinstance(supplied, RequestError):
            return supplied
        board.receive_money(min(supplied, self._towns.get_number_of_houses(player)))
        self._resource_pool.put_resources(resources_to_burn)
        self._pending.remove(player)
        if self._pending:
            return PhaseStatus.PHASE_CONTINUES
        return self._finish_phase()

    def get_state(self) -> str:
        return json.dumps({
            "phase": "bureaucracy",
            "waiting_for": [x.name.lower() for x in self._pending],
        })

    def _finish_phase(self) -> PhaseStatus:
        if self._towns.get_max_number_of_houses() >= self._houses_to_end_game:
            return PhaseStatus.GAME_ENDS
        self._resource_market.refill()
        self._power_plant_market.prepare_next_turn()
        return PhaseStatus.PHASE_ENDS
