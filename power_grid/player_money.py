from power_grid.simple_types import PlayerColor


class PlayerMoney:
    STARTING_MONEY = 50
    PAYOUT: tuple[int, ...] = (
        10, 22, 33, 44, 54, 64, 73, 82, 90, 98, 105,
        112, 118, 124, 129, 134, 138, 142, 145, 148, 150,
    )

    _color: PlayerColor
    _money: int

    def __init__(self, color: PlayerColor,
                 starting_money: int = STARTING_MONEY):
        assert starting_money >= 0
        self._color = color
        self._money = starting_money

    @property
    def color(self) -> PlayerColor:
        return self._color

    @property
    def money(self) -> int:
        return self._money

    def has_enough_money(self, amount: int) -> bool:
        return self._money >= amount

    def receive_money(self, number_of_towns: int) -> None:
        assert number_of_towns >= 0
        capped = min(number_of_towns, len(PlayerMoney.PAYOUT) - 1)
        self._money += PlayerMoney.PAYOUT[capped]

    def spend_money(self, amount: int) -> None:
        assert 0 <= amount <= self._money
        self._money -= amount
