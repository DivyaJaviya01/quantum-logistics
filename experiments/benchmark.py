"""Systematic benchmark for TSP solvers.

Small-N mode (default): Brute-Force + GA (+ optional QAOA), gap vs optimum.
    python -m experiments.benchmark --trials 10 --max-cities 9 --quick

Scale mode: pure GA vs Memetic (GA+2-opt) vs multi-start 2-opt at
10-50 cities. Brute-force is skipped (factorial explosion); methods are
compared against the best distance found (gap_vs_best).
    python -m experiments.benchmark --scale --trials 5
"""

import argparse
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np

from core.city_generator import generate_cities
from algorithms.tsp_bruteforce import solve_tsp_bruteforce
from algorithms.genetic_algorithm import (
    solve_tsp_genetic, create_random_route, is_valid_route,
)
from algorithms.memetic import solve_tsp_memetic
from algorithms.two_opt import two_opt_improve
from utils.metrics import optimality_gap

from algorithms.qaoa import solve_tsp_qaoa, MAX_CITIES_EXACT

HAS_QAOA = True
BF_LIMIT = 10  # brute-force refused above this N ((N-1)! explosion)


def solver_seed_for(map_seed, tag):
    """Derive a solver RNG seed from the map seed.

    Deterministic per (map, solver): rerunning the benchmark reproduces
    every run bit-for-bit, independent of execution order or parallelism.
    """
    return (map_seed * 31 + hash(tag)) % (2 ** 31)


def run_single(n_cities, seed, ga_params):
    """Run BF + GA on one small-N instance. Returns list of record dicts."""
    cities = generate_cities(n=n_cities, seed=seed)

    # Brute-force (exact baseline, deterministic -> solver_seed -1)
    t0 = time.perf_counter()
    bf_route, bf_dist = solve_tsp_bruteforce(cities)
    bf_time = (time.perf_counter() - t0) * 1000.0

    records = [{
        "algorithm": "brute_force",
        "n_cities": n_cities,
        "seed": seed,
        "solver_seed": -1,
        "distance": float(bf_dist),
        "time_ms": float(bf_time),
        "gap": 0.0,
        "route": "-".join(map(str, bf_route)),
    }]

    # GA runs (each with its own derived seed -> reproducible)
    for cfg_name, params in ga_params.items():
        sseed = solver_seed_for(seed, f"ga_{cfg_name}")
        t0 = time.perf_counter()
        ga_route, ga_dist, history = solve_tsp_genetic(
            cities, seed=sseed, **params)
        ga_time = (time.perf_counter() - t0) * 1000.0
        records.append({
            "algorithm": f"ga_{cfg_name}",
            "n_cities": n_cities,
            "seed": seed,
            "solver_seed": sseed,
            "distance": float(ga_dist),
            "time_ms": float(ga_time),
            "gap": float(optimality_gap(ga_dist, bf_dist)),
            "route": "-".join(map(str, ga_route)),
            "history_len": len(history),
        })

    return records


def run_scale_single(n_cities, seed, ga_params, n_restarts=20):
    """Run pure GA vs Memetic vs multi-start 2-opt on one large-N instance.

    No optimum exists here, so gap is measured vs the best distance found
    by any method on that instance (gap_vs_best).
    """
    import random as _random
    cities = generate_cities(n=n_cities, seed=seed)
    cands = []  # (algorithm, route, distance, time_ms, solver_seed)

    # 1. Pure GA
    sseed = solver_seed_for(seed, "pure_ga")
    t0 = time.perf_counter()
    ga_route, ga_dist, _ = solve_tsp_genetic(
        cities, seed=sseed, **ga_params)
    cands.append(("pure_ga", ga_route, ga_dist,
                  (time.perf_counter() - t0) * 1000.0, sseed))

    # 2. Memetic (GA + 2-opt polish)
    sseed_m = solver_seed_for(seed, "memetic")
    t0 = time.perf_counter()
    m_route, m_dist, info = solve_tsp_memetic(
        cities, seed=sseed_m, **ga_params)
    cands.append(("memetic", m_route, m_dist,
                  (time.perf_counter() - t0) * 1000.0, sseed_m))

    # 3. Multi-start 2-opt (random routes, polish each, keep best)
    sseed_t = solver_seed_for(seed, "two_opt")
    rng = _random.Random(sseed_t)
    t0 = time.perf_counter()
    best_r, best_d = None, float("inf")
    for _ in range(n_restarts):
        r = create_random_route(n_cities, rng)
        r, d, _ = two_opt_improve(cities, r)
        if d < best_d:
            best_r, best_d = r, d
    cands.append((f"two_opt_x{n_restarts}", best_r, best_d,
                  (time.perf_counter() - t0) * 1000.0, sseed_t))

    ref = min(d for _, _, d, _, _ in cands)
    records = [{
        "algorithm": algo,
        "n_cities": n_cities,
        "seed": seed,
        "solver_seed": sseed,
        "distance": float(d),
        "time_ms": float(t),
        "gap_vs_best": float(optimality_gap(d, ref)),
        "route": "-".join(map(str, r)),
    } for algo, r, d, t, sseed in cands]
    return records


def main():
    parser = argparse.ArgumentParser(description="TSP solver benchmark")
    parser.add_argument("--trials", type=int, default=10)
    parser.add_argument("--min-cities", type=int, default=4)
    parser.add_argument("--max-cities", type=int, default=9)
    parser.add_argument("--quick", action="store_true",
                        help="Use small GA params for speed")
    parser.add_argument("--include-qaoa", action="store_true",
                        help="Also run QAOA (only for N<=5, slower)")
    parser.add_argument("--scale", action="store_true",
                        help="Large-N mode: GA vs Memetic vs 2-opt "
                             "(sizes 10/20/30/40/50, no brute-force)")
    parser.add_argument("--out", type=str, default="results/benchmark_results.csv")
    args = parser.parse_args()

    if args.scale:
        sizes = [10, 20, 30, 40, 50]
        ga_params = dict(population_size=60, generations=120,
                         mutation_rate=0.05)
        runner = lambda n, s: run_scale_single(n, s, ga_params)
        out = args.out if args.out != "results/benchmark_results.csv" \
            else "results/benchmark_scale.csv"
        group_col = "gap_vs_best"
    else:
        if args.max_cities > BF_LIMIT:
            raise ValueError(
                f"Brute-force refused above N={BF_LIMIT} "
                f"({BF_LIMIT - 1}! routes already). Use --scale for large N.")
        if args.quick:
            ga_params = {
                "default": dict(population_size=30, generations=50,
                                mutation_rate=0.05),
            }
        else:
            ga_params = {
                "default": dict(population_size=50, generations=100,
                                mutation_rate=0.05),
                "large_pop": dict(population_size=100, generations=100,
                                  mutation_rate=0.05),
                "high_mut": dict(population_size=50, generations=100,
                                 mutation_rate=0.15),
            }
        sizes = list(range(args.min_cities, args.max_cities + 1))
        runner = lambda n, s: run_single(n, s, ga_params)
        out = args.out
        group_col = "gap"

    all_records = []
    total = args.trials * len(sizes)
    done = 0
    for n in sizes:
        for t in range(args.trials):
            seed = 1000 + t * 100 + n
            all_records.extend(runner(n, seed))
            # Optional QAOA (exact sim only for small N, small-N mode only)
            if (args.include_qaoa and not args.scale
                    and HAS_QAOA and n <= MAX_CITIES_EXACT):
                cities = generate_cities(n=n, seed=seed)
                _, bf_dist = solve_tsp_bruteforce(cities)
                sseed_q = solver_seed_for(seed, "qaoa_p2")
                t0 = time.perf_counter()
                q_route, q_dist, _ = solve_tsp_qaoa(
                    cities, depth=2, maxiter=60, seed=sseed_q)
                q_time = (time.perf_counter() - t0) * 1000.0
                all_records.append({
                    "algorithm": "qaoa_p2",
                    "n_cities": n,
                    "seed": seed,
                    "solver_seed": sseed_q,
                    "distance": float(q_dist),
                    "time_ms": float(q_time),
                    "gap": float(optimality_gap(q_dist, bf_dist)),
                    "route": "-".join(map(str, q_route)),
                })
            done += 1
            print(f"[{done}/{total}] n={n} seed={seed} done")

    import pandas as pd
    df = pd.DataFrame(all_records)
    out_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), out)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"\nSaved {len(df)} records to {out_path}")
    print(df.groupby(["algorithm", "n_cities"])[group_col].mean()
          .round(2).to_string())


if __name__ == "__main__":
    main()
