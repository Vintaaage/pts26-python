from typing import Sequence
from power_grid.interfaces import (
    InterfaceStepListener, InterfaceCheckAndBumpStepTowns,
    InterfaceCheckAndBumpStepPowerPlantMarket)


class CheckAndBumpStep:
    _step: int
    _towns: InterfaceCheckAndBumpStepTowns
    _power_plant_market: InterfaceCheckAndBumpStepPowerPlantMarket
    _houses_needed_for_step2: int
    _listeners: list[InterfaceStepListener]

    def __init__(self, towns: InterfaceCheckAndBumpStepTowns,
                 power_plant_market: InterfaceCheckAndBumpStepPowerPlantMarket,
                 houses_needed_for_step2: int,
                 listeners: Sequence[InterfaceStepListener]):
        assert houses_needed_for_step2 > 0
        self._step = 1
        self._towns = towns
        self._power_plant_market = power_plant_market
        self._houses_needed_for_step2 = houses_needed_for_step2
        self._listeners = list(listeners)

    def get_step(self) -> int:
        return self._step

    def check_and_bump_to_step2(self) -> None:
        if self._step != 1:
            return
        if self._towns.get_max_number_of_houses() >= self._houses_needed_for_step2:
            self._start_step2()

    def check_and_bump_to_step3(self) -> None:
        if self._step == 3:
            return
        if self._power_plant_market.is_step3_start():
            self._start_step3()

    def _start_step2(self) -> None:
        self._step = 2
        for listener in self._listeners:
            listener.start_step2()

    def _start_step3(self) -> None:
        self._step = 3
        for listener in self._listeners:
            listener.start_step3()
