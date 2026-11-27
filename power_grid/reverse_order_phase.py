from typing import Collection, Sequence
from power_grid.simple_types import PhaseStatus, PlayerColor, RequestError


class ReverseOrderPhase:
    _players: set[PlayerColor]
    _remaining: list[PlayerColor]

    def __init__(self, players: Collection[PlayerColor]):
        self._players = set(players)
        self._remaining = []

    def start_phase(self, player_order: Sequence[PlayerColor]) -> None:
        assert len(set(player_order)) == len(player_order)
        assert set(player_order) == self._players
        self._remaining = list(reversed(player_order))

    def current_player(self) -> PlayerColor | None:
        return self._remaining[0] if self._remaining else None

    def _check_turn(self, player: PlayerColor) -> RequestError | None:
        if player != self.current_player():
            return RequestError(f"It is not the turn of {player.name.lower()}")
        return None

    def _finish_turn(self) -> PhaseStatus:
        self._remaining.pop(0)
        if self._remaining:
            return PhaseStatus.PHASE_CONTINUES
        return PhaseStatus.PHASE_ENDS
