from collections import Counter
from itertools import combinations
from typing import Sequence
from power_grid.simple_types import PowerPlant, Resource


def can_power_all(resources: Sequence[Resource],
                  power_plants: Sequence[PowerPlant]) -> bool:
    available = Counter(resources)
    for size in range(1, len(power_plants) + 1):
        for subset in combinations(power_plants, size):
            demand = sum(plant.resource_amount for plant in subset)
            accepted = {x for plant in subset
                        for x in plant.accepted_resources}
            if demand > sum(available[x] for x in accepted):
                return False
    return True


class MaximumNumberOfUsablePowerPlants:
    def number_of_suppliable_towns(
            self, resources: Sequence[Resource],
            power_plants: Sequence[PowerPlant]) -> int:
        best = 0
        for size in range(len(power_plants) + 1):
            for subset in combinations(power_plants, size):
                if can_power_all(resources, subset):
                    best = max(best,
                               sum(x.number_of_cities for x in subset))
        return best
