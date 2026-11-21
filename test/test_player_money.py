import unittest

from power_grid.player_money import PlayerMoney
from power_grid.simple_types import PlayerColor


class TestPlayerMoney(unittest.TestCase):
    def setUp(self) -> None:
        self.player = PlayerMoney(PlayerColor.RED)

    def test_starts_with_fifty(self) -> None:
        self.assertEqual(self.player.money, 50)
        self.assertEqual(self.player.color, PlayerColor.RED)

    def test_has_enough_money(self) -> None:
        self.assertTrue(self.player.has_enough_money(50))
        self.assertFalse(self.player.has_enough_money(51))

    def test_spend_money(self) -> None:
        self.player.spend_money(20)
        self.assertEqual(self.player.money, 30)

    def test_spend_all_money(self) -> None:
        self.player.spend_money(50)
        self.assertEqual(self.player.money, 0)

    def test_cannot_overspend(self) -> None:
        with self.assertRaises(AssertionError):
            self.player.spend_money(51)

    def test_receive_money_for_zero_towns(self) -> None:
        self.player.receive_money(0)
        self.assertEqual(self.player.money, 60)

    def test_receive_money_for_some_towns(self) -> None:
        self.player.receive_money(7)
        self.assertEqual(self.player.money, 50 + 82)

    def test_receive_money_is_capped_at_twenty_towns(self) -> None:
        self.player.receive_money(20)
        self.assertEqual(self.player.money, 200)
        other = PlayerMoney(PlayerColor.BLUE, 0)
        other.receive_money(25)
        self.assertEqual(other.money, 150)

    def test_custom_starting_money(self) -> None:
        self.assertEqual(PlayerMoney(PlayerColor.GREEN, 7).money, 7)
