"""Scale test: pure GA vs Memetic (GA + 2-opt) at 10-50 cities.

Run from quantum-logistics/:
    python test_memetic.py
"""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.city_generator import generate_cities
from algorithms.genetic_algorithm import solve_tsp_genetic
from algorithms.memetic import solve_tsp_memetic
from algorithms.two_opt import two_opt_improve, count_crossings


def main():
    print(f"{'N':>4} | {'Pure GA':>10} | {'Memetic':>10} | {'Gain':>8} | "
          f"{'GA time':>8} | {'Mem time':>8} | {'X before->after'}")
    print("-" * 80)
    for n in [10, 20, 30, 40, 50]:
        cities = generate_cities(n=n, seed=99)

        t0 = time.perf_counter()
        _, ga_dist, _ = solve_tsp_genetic(
            cities, population_size=100, generations=200, mutation_rate=0.05)
        ga_ms = (time.perf_counter() - t0) * 1000

        t0 = time.perf_counter()
        m_route, m_dist, info = solve_tsp_memetic(
            cities, population_size=100, generations=200, mutation_rate=0.05)
        m_ms = (time.perf_counter() - t0) * 1000

        gain = (ga_dist - m_dist) / ga_dist * 100
        x_before = count_crossings(cities, m_route)  # after polish (~0)
        print(f"{n:>4} | {ga_dist:>10.1f} | {m_dist:>10.1f} | {gain:>7.2f}% | "
              f"{ga_ms:>7.0f}ms | {m_ms:>7.0f}ms | polish_gain={info['polish_gain']:.1f}")


if __name__ == "__main__":
    main()
