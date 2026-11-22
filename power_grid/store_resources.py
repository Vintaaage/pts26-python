from collections import Counter
from itertools import combinations
from typing import Sequence
from power_grid.simple_types import PowerPlant, Resource


class StoreResources:
    STORAGE_FACTOR = 2

    def can_store_resources(self, resources: Sequence[Resource],
                            power_plants: Sequence[PowerPlant]) -> bool:
        needed = Counter(resources)
        for size in range(1, len(Resource) + 1):
            for subset in combinations(Resource, size):
                demand = sum(needed[x] for x in subset)
                capacity = sum(
                    StoreResources.STORAGE_FACTOR * plant.resource_amount
                    for plant in power_plants
                    if any(x in plant.accepted_resources for x in subset))
                if demand > capacity:
                    return False
        return True
