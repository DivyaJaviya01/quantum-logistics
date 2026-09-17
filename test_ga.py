"""Test script for the Genetic Algorithm TSP solver.

Run from the quantum-logistics directory:
    python test_ga.py
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.city_generator import generate_cities
from core.distance import calculate_distance
from algorithms.tsp_bruteforce import solve_tsp_bruteforce
from algorithms.genetic_algorithm import solve_tsp_genetic, is_valid_route


def main():
    print("=" * 60)
    print("GENETIC ALGORITHM TSP TEST")
    print("=" * 60)

    # Generate cities with a fixed seed for reproducibility
    cities = generate_cities(n=5, seed=42)
    print(f"\nGenerated {len(cities)} cities:")
    for i, (x, y) in enumerate(cities):
        print(f"  City {i+1}: ({x:.2f}, {y:.2f})")

    # Run brute-force solver
    print("\n--- Brute-Force Solver ---")
    bf_route, bf_distance = solve_tsp_bruteforce(cities)
    bf_route_cities = [r + 1 for r in bf_route]
    print(f"Best route: {' -> '.join(map(str, bf_route_cities))} -> {bf_route_cities[0]}")
    print(f"Best distance: {bf_distance:.2f}")

    # Run GA solver
    print("\n--- Genetic Algorithm Solver ---")
    ga_route, ga_distance, history = solve_tsp_genetic(
        cities,
        population_size=50,
        generations=100,
        mutation_rate=0.05
    )
    ga_route_cities = [r + 1 for r in ga_route]
    print(f"Best route: {' -> '.join(map(str, ga_route_cities))} -> {ga_route_cities[0]}")
    print(f"Best distance: {ga_distance:.2f}")
    print(f"Distance per generation (first 10): {[f'{d:.1f}' for d in history[:10]]}")
    print(f"Distance per generation (last 10):  {[f'{d:.1f}' for d in history[-10:]]}")

    # Validate the GA route
    print("\n--- Validation ---")
    valid = is_valid_route(ga_route, len(cities))
    print(f"GA route is valid: {valid}")

    # Compare results
    print("\n--- Comparison ---")
    print(f"Brute-force distance: {bf_distance:.2f}")
    print(f"GA distance:          {ga_distance:.2f}")
    diff = ga_distance - bf_distance
    print(f"Difference:           {diff:.2f}")
    if abs(diff) < 0.01:
        print("GA found the OPTIMAL route!")
    else:
        pct = (diff / bf_distance) * 100
        print(f"GA is {pct:.1f}% longer than optimal")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
