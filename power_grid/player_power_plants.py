from typing import Sequence
from power_grid.maximum_number_of_usable_power_plants import (
    MaximumNumberOfUsablePowerPlants)
from power_grid.simple_types import (
    PowerPlant, PowerPlantNumber, RequestError, Resource)
from power_grid.store_resources import StoreResources
from power_grid.use_power_plants import UsePowerPlants


class PlayerPowerPlants:
    MAX_POWER_PLANTS = 3

    _power_plants: list[PowerPlant]
    _store_resources: StoreResources
    _maximum: MaximumNumberOfUsablePowerPlants
    _use_power_plants: UsePowerPlants

    def __init__(self, power_plants: Sequence[PowerPlant] = ()):
        assert len(power_plants) <= PlayerPowerPlants.MAX_POWER_PLANTS
        self._power_plants = list(power_plants)
        self._store_resources = StoreResources()
        self._maximum = MaximumNumberOfUsablePowerPlants()
        self._use_power_plants = UsePowerPlants()

    @property
    def power_plants(self) -> list[PowerPlant]:
        return list(self._power_plants)

    def best_power_plant(self) -> PowerPlantNumber:
        return PowerPlantNumber(
            max((x.number.number for x in self._power_plants), default=0))

    def receive_power_plant(self, power_plant: PowerPlant) -> bool:
        if len(self._power_plants) >= PlayerPowerPlants.MAX_POWER_PLANTS:
            return False
        assert power_plant.number not in [
            x.number for x in self._power_plants]
        self._power_plants.append(power_plant)
        return True

    def remove_power_plant(
            self, ppn: PowerPlantNumber,
            new_resources: Sequence[Resource]) -> RequestError | None:
        remaining = [x for x in self._power_plants if x.number != ppn]
        if len(remaining) == len(self._power_plants):
            return RequestError(f"You do not own power plant {ppn.number}")
        if not self._store_resources.can_store_resources(
                new_resources, remaining):
            return RequestError("The remaining power plants cannot store these resources")
        self._power_plants = remaining
        return None

    def number_of_connectable_cities(
            self, resources: Sequence[Resource]) -> int:
        return self._maximum.number_of_suppliable_towns(
            resources, self._power_plants)

    def can_store_resources(self, resources: Sequence[Resource]) -> bool:
        return self._store_resources.can_store_resources(
            resources, self._power_plants)

    def use_power_plant(
            self, ppns: Sequence[PowerPlantNumber],
            resources_to_burn: Sequence[Resource]) -> int | RequestError:
        selected: list[PowerPlant] = []
        for ppn in ppns:
            owned = [x for x in self._power_plants if x.number == ppn]
            if not owned:
                return RequestError(f"You do not own power plant {ppn.number}")
            selected.append(owned[0])
        return self._use_power_plants.number_of_suppliable_towns(
            resources_to_burn, selected)
