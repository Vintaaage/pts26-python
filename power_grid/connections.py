from typing import Sequence

INFINITY = 10**9


class Connections:
    _distance: dict[str, dict[str, int]]

    def __init__(self, distances: Sequence[tuple[str, str, int]]):
        towns = {name for a, b, _ in distances for name in (a, b)}
        self._distance = {a: {b: 0 if a == b else INFINITY for b in towns}
                          for a in towns}
        for first, second, cost in distances:
            assert cost >= 0
            if cost < self._distance[first][second]:
                self._distance[first][second] = cost
                self._distance[second][first] = cost
        for middle in towns:
            for first in towns:
                for second in towns:
                    via = self._distance[first][middle] \
                        + self._distance[middle][second]
                    if via < self._distance[first][second]:
                        self._distance[first][second] = via

    def calculate_connecting_cost(self, from_towns: Sequence[str],
                                  to_towns: Sequence[str]) -> int:
        assert all(x in self._distance for x in from_towns)
        assert all(x in self._distance for x in to_towns)
        network: list[str] = list(from_towns)
        remaining: list[str] = list(to_towns)
        total = 0
        if not network and remaining:
            network.append(remaining.pop(0))
        while remaining:
            cost, index = min((self._cost_to_network(network, town), i)
                              for i, town in enumerate(remaining))
            assert cost < INFINITY
            total += cost
            network.append(remaining.pop(index))
        return total

    def _cost_to_network(self, network: Sequence[str], town: str) -> int:
        return min(self._distance[x][town] for x in network)
