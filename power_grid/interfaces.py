# pylint: disable=unused-argument, duplicate-code
from typing import Sequence
from power_grid.simple_types import (Resource, PlayerColor, PowerPlantNumber, RequestError)


class InterfaceResourcePoolResourceMarket:
    def can_take_resources_from_storage_space(self, resources: Sequence[Resource]) -> bool:
        assert False

    def get_from_storage_space(self, resources: Sequence[Resource]) -> None:
        assert False

    def take_resources(self, resources: Sequence[Resource]) -> list[Resource]:
        assert False

    def to_string(self) -> str:
        assert False

class InterfaceStepListener:
    def start_step2(self) -> None:
        assert False

    def start_step3(self) -> None:
        assert False


class InterfaceCheckAndBumpStepTowns:
    def get_max_number_of_houses(self) -> int:
        assert False


class InterfaceCheckAndBumpStepPowerPlantMarket:
    def is_step3_start(self) -> bool:
        assert False

class InterfaceDeterminePlayerOrderTowns:
    def get_number_of_houses(self, player: PlayerColor) -> int:
        assert False


class InterfaceDeterminePlayerOrderPlayerBoard:
    def best_power_plant_number(self) -> PowerPlantNumber:
        assert False

    def outstanding_money(self) -> int:
        assert False

    def number_of_connectable_cities(self) -> int:
        assert False

class InterfaceBuyingResourcesResourceMarket:
    def get_price(self, desired: list[Resource]) -> int | None:
        assert False

    def take_resources(self, resources: list[Resource]) -> None:
        assert False

class InterfaceBureaucracyTowns:
    def get_number_of_houses(self, player: PlayerColor) -> int:
        assert False

class InterfaceBureaucracyResourcePool:
    def put_resources(self, resources: Sequence[Resource]) -> None:
        assert False


class InterfaceBureaucracyResourceMarket:
    def refill(self) -> None:
        assert False


class InterfaceBureaucracyPowerPlantMarket:
    def prepare_next_turn(self) -> None:
        assert False

class InterfaceBuildingHousesTowns:
    def buy_houses(self, player: PlayerColor, town_names: Sequence[str],
                   max_money: int) -> int | RequestError:
        assert False

    def get_max_number_of_houses(self) -> int:
        assert False
