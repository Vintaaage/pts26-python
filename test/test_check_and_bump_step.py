import unittest

from power_grid.check_and_bump_step import CheckAndBumpStep
from power_grid.interfaces import (
    InterfaceStepListener, InterfaceCheckAndBumpStepTowns,
    InterfaceCheckAndBumpStepPowerPlantMarket)


class TownsFake(InterfaceCheckAndBumpStepTowns):
    max_houses: int

    def __init__(self) -> None:
        self.max_houses = 0

    def get_max_number_of_houses(self) -> int:
        return self.max_houses


class PowerPlantMarketFake(InterfaceCheckAndBumpStepPowerPlantMarket):
    step3_start: bool

    def __init__(self) -> None:
        self.step3_start = False

    def is_step3_start(self) -> bool:
        return self.step3_start


class ListenerFake(InterfaceStepListener):
    calls: list[str]

    def __init__(self) -> None:
        self.calls = []

    def start_step2(self) -> None:
        self.calls.append("step2")

    def start_step3(self) -> None:
        self.calls.append("step3")


class TestCheckAndBumpStep(unittest.TestCase):
    def setUp(self) -> None:
        self.towns = TownsFake()
        self.market = PowerPlantMarketFake()
        self.first = ListenerFake()
        self.second = ListenerFake()
        self.step = CheckAndBumpStep(
            self.towns, self.market, 7, [self.first, self.second])

    def test_starts_in_step_one(self) -> None:
        self.assertEqual(self.step.get_step(), 1)

    def test_no_bump_below_threshold(self) -> None:
        self.towns.max_houses = 6
        self.step.check_and_bump_to_step2()
        self.assertEqual(self.step.get_step(), 1)
        self.assertEqual(self.first.calls, [])

    def test_bump_to_step2_at_threshold(self) -> None:
        self.towns.max_houses = 7
        self.step.check_and_bump_to_step2()
        self.assertEqual(self.step.get_step(), 2)
        self.assertEqual(self.first.calls, ["step2"])
        self.assertEqual(self.second.calls, ["step2"])

    def test_step2_is_started_only_once(self) -> None:
        self.towns.max_houses = 9
        self.step.check_and_bump_to_step2()
        self.step.check_and_bump_to_step2()
        self.assertEqual(self.first.calls, ["step2"])

    def test_no_bump_to_step3_without_step3_card(self) -> None:
        self.step.check_and_bump_to_step3()
        self.assertEqual(self.step.get_step(), 1)
        self.assertEqual(self.first.calls, [])

    def test_bump_from_step2_to_step3(self) -> None:
        self.towns.max_houses = 7
        self.step.check_and_bump_to_step2()
        self.market.step3_start = True
        self.step.check_and_bump_to_step3()
        self.assertEqual(self.step.get_step(), 3)
        self.assertEqual(self.first.calls, ["step2", "step3"])

    def test_step3_is_started_only_once(self) -> None:
        self.market.step3_start = True
        self.step.check_and_bump_to_step3()
        self.step.check_and_bump_to_step3()
        self.assertEqual(self.first.calls, ["step2", "step3"])

    def test_step3_before_step2_performs_both_changes(self) -> None:
        self.market.step3_start = True
        self.step.check_and_bump_to_step3()
        self.assertEqual(self.step.get_step(), 3)
        self.assertEqual(self.first.calls, ["step2", "step3"])

    def test_no_step2_after_step3(self) -> None:
        self.market.step3_start = True
        self.step.check_and_bump_to_step3()
        self.towns.max_houses = 10
        self.step.check_and_bump_to_step2()
        self.assertEqual(self.step.get_step(), 3)
        self.assertEqual(self.first.calls, ["step2", "step3"])

if __name__ == "__main__":
    unittest.main()
