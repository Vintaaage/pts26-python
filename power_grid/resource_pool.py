import json
from collections import Counter
from typing import Sequence

from power_grid.interfaces import InterfaceResourcePoolResourceMarket
from power_grid.simple_types import Resource


class ResourcePool(InterfaceResourcePoolResourceMarket):
    _resources: dict[Resource, int]

    def __init__(self, resources: Sequence[Resource] = ()):
        counts = Counter(resources)
        self._resources = {x: counts[x] for x in Resource}

    def can_take_resources_from_storage_space(
            self, resources: Sequence[Resource]) -> bool:
        counts = Counter(resources)
        return all(counts[x] <= self._resources[x] for x in Resource)

    def get_from_storage_space(self, resources: Sequence[Resource]) -> None:
        assert self.can_take_resources_from_storage_space(resources)
        for resource in resources:
            self._resources[resource] -= 1

    def take_resources(self, resources: Sequence[Resource]) -> list[Resource]:
        taken: list[Resource] = []
        for resource in resources:
            if self._resources[resource] > 0:
                self._resources[resource] -= 1
                taken.append(resource)
        return taken

    def put_resources(self, resources: Sequence[Resource]) -> None:
        for resource in resources:
            self._resources[resource] += 1

    def to_string(self) -> str:
        return json.dumps({
            "coal": self._resources[Resource.COAL],
            "oil": self._resources[Resource.OIL],
            "garbage": self._resources[Resource.GARBAGE],
            "uranium": self._resources[Resource.URANIUM],
        })
