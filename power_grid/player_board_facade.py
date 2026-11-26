import json
from typing import Sequence
from power_grid.interfaces import InterfaceDeterminePlayerOrderPlayerBoard
from power_grid.player_money import PlayerMoney
from power_grid.player_power_plants import PlayerPowerPlants
from power_grid.player_resources import PlayerResources
from power_grid.simple_types import (
    PlayerColor, PowerPlant, PowerPlantNumber, RequestError, Resource)


class PlayerBoardFacade(InterfaceDeterminePlayerOrderPlayerBoard):
    _money: PlayerMoney
    _power_plants: PlayerPowerPlants
    _resources: PlayerResources

    def __init__(self, color: PlayerColor,
                 money: int = PlayerMoney.STARTING_MONEY):
        self._money = PlayerMoney(color, money)
        self._power_plants = PlayerPowerPlants()
        self._resources = PlayerResources(self._power_plants)

    @property
    def color(self) -> PlayerColor:
        return self._money.color

    @property
    def power_plants(self) -> list[PowerPlant]:
        return self._power_plants.power_plants

    @property
    def resources(self) -> list[Resource]:
        return self._resources.resources

    def best_power_plant_number(self) -> PowerPlantNumber:
        return self._power_plants.best_power_plant()

    def outstanding_money(self) -> int:
        return self._money.money

    def has_enough_money(self, amount: int) -> bool:
        return self._money.has_enough_money(amount)

    def spend_money(self, amount: int) -> None:
        self._money.spend_money(amount)

    def receive_money(self, number_of_towns: int) -> None:
        self._money.receive_money(number_of_towns)

    def number_of_connectable_cities(self) -> int:
        return self._resources.number_of_connectable_cities()

    def receive_power_plant(self, power_plant: PowerPlant, price: int) -> bool:
        assert self.has_enough_money(price)
        if not self._power_plants.receive_power_plant(power_plant):
            return False
        self._money.spend_money(price)
        return True

    def remove_power_plant(
            self, ppn: PowerPlantNumber,
            removed_resources: Sequence[Resource]) -> RequestError | None:
        return self._resources.remove_power_plant(ppn, removed_resources)

    def buy_resources(
            self, resources: Sequence[Resource]) -> RequestError | None:
        return self._resources.buy_resources(resources)

    def use_power_plants(
            self, ppns: Sequence[PowerPlantNumber],
            resources_to_burn: Sequence[Resource]) -> int | RequestError:
        return self._resources.use_power_plant(ppns, resources_to_burn)

    def state(self) -> str:
        return json.dumps({
            "color": self.color.name.lower(),
            "money": self.outstanding_money(),
            "power_plants": [x.number.number for x in self.power_plants],
            "resources": [x.name.lower() for x in self.resources],
        })
