from collections import Counter
from typing import Sequence
from power_grid.player_power_plants import PlayerPowerPlants
from power_grid.simple_types import PowerPlantNumber, RequestError, Resource


class PlayerResources:
    _resources: list[Resource]
    _power_plants: PlayerPowerPlants

    def __init__(self, power_plants: PlayerPowerPlants,
                 resources: Sequence[Resource] = ()):
        assert power_plants.can_store_resources(resources)
        self._power_plants = power_plants
        self._resources = list(resources)

    @property
    def resources(self) -> list[Resource]:
        return list(self._resources)

    def buy_resources(
            self, resources: Sequence[Resource]) -> RequestError | None:
        new_resources = self._resources + list(resources)
        if not self._power_plants.can_store_resources(new_resources):
            return RequestError("Not enough storage space for the resources")
        self._resources = new_resources
        return None

    def remove_power_plant(
            self, ppn: PowerPlantNumber,
            removed_resources: Sequence[Resource]) -> RequestError | None:
        available = Counter(self._resources)
        if Counter(removed_resources) - available:
            return RequestError("You do not have the resources to discard")
        new_resources = list((available - Counter(removed_resources)).elements())
        error = self._power_plants.remove_power_plant(ppn, new_resources)
        if error is None:
            self._resources = new_resources
        return error

    def number_of_connectable_cities(self) -> int:
        return self._power_plants.number_of_connectable_cities(
            self._resources)

    def use_power_plant(
            self, ppns: Sequence[PowerPlantNumber],
            resources_to_burn: Sequence[Resource]) -> int | RequestError:
        available = Counter(self._resources)
        burned = Counter(resources_to_burn)
        if burned - available:
            return RequestError("You do not have the resources to burn")
        result = self._power_plants.use_power_plant(ppns, resources_to_burn)
        if isinstance(result, RequestError):
            return result
        self._resources = list((available - burned).elements())
        return result
