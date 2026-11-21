import unittest

from power_grid.connections import Connections


class TestConnections(unittest.TestCase):
    def setUp(self) -> None:
        self.connections = Connections([
            ("A", "B", 5), ("B", "C", 3), ("A", "C", 10), ("C", "D", 4),
            ("X", "Y", 1),
        ])

    def cost(self, from_towns: list[str], to_towns: list[str]) -> int:
        return self.connections.calculate_connecting_cost(
            from_towns, to_towns)

    def test_nothing_to_build_is_free(self) -> None:
        self.assertEqual(self.cost(["A"], []), 0)
        self.assertEqual(self.cost([], []), 0)

    def test_first_house_is_free(self) -> None:
        self.assertEqual(self.cost([], ["D"]), 0)

    def test_neighbouring_town(self) -> None:
        self.assertEqual(self.cost(["A"], ["B"]), 5)

    def test_shortest_path_is_used(self) -> None:
        self.assertEqual(self.cost(["A"], ["C"]), 8)

    def test_already_connected_town_is_free(self) -> None:
        self.assertEqual(self.cost(["A"], ["A"]), 0)

    def test_new_towns_extend_the_network(self) -> None:
        self.assertEqual(self.cost(["A"], ["B", "C"]), 8)
        self.assertEqual(self.cost(["A"], ["C", "B"]), 8)
        self.assertEqual(self.cost(["A"], ["C", "D"]), 12)

    def test_cheapest_owned_town_is_used(self) -> None:
        self.assertEqual(self.cost(["A", "D"], ["C"]), 4)

    def test_first_house_free_then_connections_paid(self) -> None:
        self.assertEqual(self.cost([], ["B", "C", "D"]), 7)
        self.assertEqual(self.cost([], ["A", "C"]), 8)

    def test_cheapest_parallel_connection_is_used(self) -> None:
        connections = Connections([("A", "B", 5), ("B", "A", 3)])
        self.assertEqual(connections.calculate_connecting_cost(["A"], ["B"]),
                         3)

    def test_unknown_town_fails(self) -> None:
        with self.assertRaises(AssertionError):
            self.cost(["A"], ["Z"])
        with self.assertRaises(AssertionError):
            self.cost(["Z"], ["A"])

    def test_unreachable_town_fails(self) -> None:
        with self.assertRaises(AssertionError):
            self.cost(["A"], ["X"])


if __name__ == "__main__":
    unittest.main()
