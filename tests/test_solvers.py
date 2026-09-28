"""Solver test suite: validity, optimality, non-regression, reproducibility.

Run with:  pytest tests/ -q        (or)  python tests/test_solvers.py
"""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.city_generator import generate_cities
from core.distance import calculate_distance
from algorithms.tsp_bruteforce import solve_tsp_bruteforce
from algorithms.genetic_algorithm import (
    solve_tsp_genetic, is_valid_route, order_crossover,
)
from algorithms.two_opt import two_opt_improve, two_opt_swap
from algorithms.memetic import solve_tsp_memetic
from utils.metrics import optimality_gap


def test_distance_known_triangle():
    cities = np.array([[0.0, 0.0], [3.0, 0.0], [0.0, 4.0]])
    # 0->1 (3) + 1->2 (5) + 2->0 (4) = 12
    assert abs(calculate_distance(cities, [0, 1, 2]) - 12.0) < 1e-9


def test_city_generator_reproducible():
    a = generate_cities(n=6, seed=11)
    b = generate_cities(n=6, seed=11)
    assert a.shape == (6, 2)
    assert bool(((a >= 0) & (a <= 100)).all())
    assert np.array_equal(a, b)


def test_bruteforce_is_optimal():
    cities = generate_cities(n=5, seed=3)
    route, dist = solve_tsp_bruteforce(cities)
    assert is_valid_route(route, 5)
    # Exhaustive re-check: no route beats it
    from itertools import permutations
    for perm in permutations(range(1, 5)):
        r = [0] + list(perm)
        assert calculate_distance(cities, r) >= dist - 1e-9


def test_ga_valid_and_reproducible():
    cities = generate_cities(n=8, seed=5)
    r1, d1, h1 = solve_tsp_genetic(cities, population_size=20,
                                   generations=20, seed=77)
    r2, d2, h2 = solve_tsp_genetic(cities, population_size=20,
                                   generations=20, seed=77)
    assert is_valid_route(r1, 8)
    assert r1 == r2 and d1 == d2 and h1 == h2  # bit-identical
    assert len(h1) == 20 and all(h1[i] >= h1[i + 1] - 1e-9
                                 for i in range(19))  # never regresses


def test_crossover_never_duplicates():
    import random
    rng = random.Random(0)
    p1 = [0, 3, 1, 4, 2]
    p2 = [0, 1, 4, 2, 3]
    for _ in range(50):
        child = order_crossover(p1, p2, rng)
        assert all(isinstance(c, int) for c in child)
        assert sorted(child) == [0, 1, 2, 3, 4]


def test_two_opt_never_worsens():
    cities = generate_cities(n=12, seed=9)
    import random
    rng = random.Random(1)
    route = [0] + rng.sample(range(1, 12), 11)
    before = calculate_distance(cities, route)
    improved, after, _ = two_opt_improve(cities, route)
    assert after <= before + 1e-9
    assert is_valid_route(improved, 12)
    # Swap keeps depot fixed and preserves the city set
    assert two_opt_swap([0, 1, 2, 3, 4], 2, 4) == [0, 1, 4, 3, 2]


def test_memetic_valid_and_reproducible():
    cities = generate_cities(n=10, seed=21)
    r1, d1, i1 = solve_tsp_memetic(cities, population_size=20,
                                   generations=15, seed=55)
    r2, d2, i2 = solve_tsp_memetic(cities, population_size=20,
                                   generations=15, seed=55)
    assert is_valid_route(r1, 10)
    assert r1 == r2 and d1 == d2
    assert i1["polish_gain"] >= -1e-9  # polish never hurts


def test_qaoa_valid_and_guarded():
    from algorithms.qaoa import solve_tsp_qaoa, decode_bitstring
    cities = generate_cities(n=4, seed=2)
    route, dist, info = solve_tsp_qaoa(cities, depth=1, maxiter=10)
    assert is_valid_route(route, 4)
    assert info["qubits"] == 9
    assert dist == calculate_distance(cities, route)
    # Diagnostics are proper probabilities with sane ordering
    assert 0.0 <= info["p_optimal"] <= info["p_feasible"] <= 1.0
    assert info["gap_vs_optimal"] >= -1e-9
    assert abs(info["gap_vs_optimal"]
               - (dist - info["bf_distance"]) / info["bf_distance"] * 100) < 1e-6
    # Decode always repairs to a valid route
    for k in [0, 1, 123, 511]:
        assert is_valid_route(decode_bitstring(k, 4), 4)
    # Too big -> clear error, not an OOM crash
    big = generate_cities(n=6, seed=2)
    try:
        solve_tsp_qaoa(big)
        raise AssertionError("expected ValueError for N=6")
    except ValueError:
        pass


def test_metrics_gap():
    assert optimality_gap(110.0, 100.0) == 10.0
    assert optimality_gap(100.0, 100.0) == 0.0


if __name__ == "__main__":
    fns = [(k, v) for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    failed = 0
    for name, fn in fns:
        try:
            fn()
            print(f"PASS {name}")
        except Exception as e:
            failed += 1
            print(f"FAIL {name}: {type(e).__name__}: {e}")
    print(f"\n{len(fns) - failed}/{len(fns)} passed")
    sys.exit(1 if failed else 0)
