from typing import Sequence
from power_grid.maximum_number_of_usable_power_plants import can_power_all
from power_grid.simple_types import PowerPlant, RequestError, Resource


class UsePowerPlants:
    def number_of_suppliable_towns(
            self, resources: Sequence[Resource],
            power_plants: Sequence[PowerPlant]) -> int | RequestError:
        numbers = [plant.number for plant in power_plants]
        if len(set(numbers)) != len(numbers):
            return RequestError("The same power plant is used twice")
        needed = sum(plant.resource_amount for plant in power_plants)
        if len(resources) != needed:
            return RequestError(
                f"The power plants burn {needed} resources, "
                f"but {len(resources)} were given")
        if not can_power_all(resources, power_plants):
            return RequestError(
                "The resources do not match the power plants")
        return sum(plant.number_of_cities for plant in power_plants)
