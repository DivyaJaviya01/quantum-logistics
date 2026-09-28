"""QAOA sensitivity: penalty x depth grid on one 5-city map.

Measures what the review asked for: P(feasible), P(optimal),
penalized energy vs true tour distance, and sensitivity to
penalty weight / circuit depth / optimizer budget.

Usage:
    cd quantum-logistics
    python -m experiments.qaoa_sensitivity
"""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np

from core.city_generator import generate_cities
from algorithms.qaoa import solve_tsp_qaoa, build_qubo_energies


def main():
    cities = generate_cities(n=5, seed=42)
    base_pen = float(5 * max(np.linalg.norm(cities[i] - cities[j])
                             for i in range(5) for j in range(5)))

    rows = []
    for depth in [1, 2, 3]:
        for mult in [0.5, 1.0, 2.0]:
            t0 = time.perf_counter()
            route, dist, info = solve_tsp_qaoa(
                cities, depth=depth, penalty=base_pen * mult, maxiter=60)
            ms = (time.perf_counter() - t0) * 1000.0
            rows.append({
                "depth": depth,
                "penalty_mult": mult,
                "tour_dist": round(dist, 2),
                "gap_pct": round(info["gap_vs_optimal"], 2),
                "expectation": round(info["expectation"], 1),
                "p_feasible": round(info["p_feasible"], 4),
                "p_optimal": round(info["p_optimal"], 4),
                "time_ms": round(ms, 0),
            })
            print(f"p={depth} pen=x{mult}: dist={dist:.1f} "
                  f"gap={info['gap_vs_optimal']:.1f}% "
                  f"P feas={info['p_feasible']:.3f} "
                  f"P opt={info['p_optimal']:.3f} [{ms:.0f}ms]")

    import pandas as pd
    df = pd.DataFrame(rows)
    out = os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), "results",
        "benchmark_qaoa_sensitivity.csv")
    df.to_csv(out, index=False)
    print(f"\nSaved to {out}")


if __name__ == "__main__":
    main()
