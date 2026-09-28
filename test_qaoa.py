"""Test QAOA solver vs brute-force.

Run from quantum-logistics/:
    python test_qaoa.py
"""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.city_generator import generate_cities
from algorithms.tsp_bruteforce import solve_tsp_bruteforce
from algorithms.genetic_algorithm import solve_tsp_genetic
from algorithms.qaoa import solve_tsp_qaoa


def show(name, route, dist, extra=""):
    cities = " -> ".join(str(r + 1) for r in route)
    print(f"{name:12s} route {cities} -> 1 | dist {dist:.2f} {extra}")


def main():
    for n, seed in [(4, 42), (5, 42)]:
        print(f"\n=== N={n} cities (seed={seed}) ===")
        cities = generate_cities(n=n, seed=seed)

        t0 = time.perf_counter()
        bf_route, bf_dist = solve_tsp_bruteforce(cities)
        bf_ms = (time.perf_counter() - t0) * 1000
        show("BruteForce", bf_route, bf_dist, f"[{bf_ms:.0f}ms]")

        t0 = time.perf_counter()
        ga_route, ga_dist, _ = solve_tsp_genetic(cities)
        ga_ms = (time.perf_counter() - t0) * 1000
        show("Genetic", ga_route, ga_dist,
             f"[gap {(ga_dist - bf_dist) / bf_dist * 100:.2f}% | {ga_ms:.0f}ms]")

        t0 = time.perf_counter()
        q_route, q_dist, info = solve_tsp_qaoa(cities, depth=2)
        q_ms = (time.perf_counter() - t0) * 1000
        show("QAOA(p=2)", q_route, q_dist,
             f"[gap {(q_dist - bf_dist) / bf_dist * 100:.2f}% | "
             f"{info['qubits']} qubits | top_prob {info['top_prob']:.3f} | "
             f"{q_ms:.0f}ms]")


if __name__ == "__main__":
    main()
