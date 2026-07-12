"""Coherent-stack and station-outage tests."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from oceangravity.pegs import (  # noqa: E402
    NetworkPerformance,
    coherent_network_stack,
    generate_station_outage_masks,
    pareto_optimal_networks,
)


class TestPegsNetwork(unittest.TestCase):
    def test_equal_coherent_stations_gain_sqrt_n(self) -> None:
        stack = coherent_network_stack(
            {"A": [1.0, 2.0], "B": [1.0, 2.0], "C": [1.0, 2.0], "D": [1.0, 2.0]}
        )
        self.assertEqual(stack, (2.0, 4.0))

    def test_signed_weights_and_station_identity_are_explicit(self) -> None:
        stack = coherent_network_stack(
            {"A": [1.0, 1.0], "B": [-1.0, -1.0]},
            station_weights={"A": 1.0, "B": -1.0},
        )
        self.assertAlmostEqual(stack[0], math.sqrt(2.0))
        with self.assertRaises(ValueError):
            coherent_network_stack(
                {"A": [1.0], "B": [1.0]}, station_weights={"A": 1.0}
            )

    def test_outage_masks_have_fixed_counts_and_are_deterministic(self) -> None:
        stations = tuple(f"S{index:02d}" for index in range(10))
        first = generate_station_outage_masks(stations, 0.4, 5, random_seed=42)
        second = generate_station_outage_masks(stations, 0.4, 5, random_seed=42)
        self.assertEqual(first, second)
        self.assertTrue(all(len(mask) == 6 for mask in first))
        no_outage = generate_station_outage_masks(stations, 0.0, 2, random_seed=1)
        self.assertEqual(no_outage, (stations, stations))

    def test_invalid_series_and_outage_configuration_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            coherent_network_stack({"A": [1.0], "B": [1.0, 2.0]})
        with self.assertRaises(ValueError):
            generate_station_outage_masks(["A"], 1.0, 1, random_seed=1)

    def test_pareto_front_retains_real_tradeoffs(self) -> None:
        efficient_fast = NetworkPerformance(
            "fast-expensive", ("A", "B", "C"), 240.0, 0.95, 0.5, 0.20, 3.0
        )
        efficient_cheap = NetworkPerformance(
            "slow-cheap", ("A",), 360.0, 0.90, 0.8, 0.30, 1.0
        )
        dominated = NetworkPerformance(
            "dominated", ("A", "B"), 400.0, 0.85, 1.0, 0.35, 2.0
        )
        frontier = pareto_optimal_networks(
            (dominated, efficient_cheap, efficient_fast)
        )
        self.assertEqual(
            tuple(row.network_id for row in frontier),
            ("fast-expensive", "slow-cheap"),
        )

    def test_equal_metrics_do_not_arbitrarily_remove_candidates(self) -> None:
        left = NetworkPerformance("A-design", ("A",), 300.0, 0.9, 1.0, 0.3, 1.0)
        right = NetworkPerformance("B-design", ("B",), 300.0, 0.9, 1.0, 0.3, 1.0)
        self.assertEqual(pareto_optimal_networks((right, left)), (left, right))

    def test_network_metrics_reject_invalid_values_and_duplicate_ids(self) -> None:
        with self.assertRaises(ValueError):
            NetworkPerformance("bad", ("A",), -1.0, 0.9, 0.0, 0.1, 1.0)
        with self.assertRaises(ValueError):
            NetworkPerformance("bad", ("A",), 1.0, 1.1, 0.0, 0.1, 1.0)
        row = NetworkPerformance("same", ("A",), 1.0, 0.9, 0.0, 0.1, 1.0)
        with self.assertRaises(ValueError):
            pareto_optimal_networks((row, row))
        with self.assertRaises(ValueError):
            pareto_optimal_networks(())


if __name__ == "__main__":
    unittest.main()
