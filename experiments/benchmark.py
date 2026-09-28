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


def run_budget_single(n_cities, seed, budget_s, pop_size=60,
                      n_restarts_probe=20):
    """Race all methods with the SAME wall-clock budget on one map.

    Fair comparison: each method gets exactly `budget_s` seconds.
    - pure_ga: generations calibrated from a 5-gen timing probe.
    - memetic: GA on 70% of budget + full 2-opt polish.
    - two_opt: restarts until the clock runs out.
    Returns records with actual time_ms and gap_vs_best (same budget+map).
    """
    import random as _random
    cities = generate_cities(n=n_cities, seed=seed)
    cands = []  # (algorithm, route, distance, actual_ms, solver_seed)

    # 1. Pure GA: calibrate generations to fit the budget
    sseed = solver_seed_for(seed, f"budget_ga_{budget_s}")
    t0 = time.perf_counter()
    solve_tsp_genetic(cities, population_size=pop_size, generations=5,
                      mutation_rate=0.05, seed=sseed)
    per_gen = (time.perf_counter() - t0) / 5.0
    gens_fit = max(5, int(budget_s * 0.92 / max(per_gen, 1e-6)))
    t0 = time.perf_counter()
    ga_route, ga_dist, _ = solve_tsp_genetic(
        cities, population_size=pop_size, generations=gens_fit,
        mutation_rate=0.05, seed=sseed)
    cands.append(("pure_ga", ga_route, ga_dist,
                  (time.perf_counter() - t0) * 1000.0, sseed))

    # 2. Memetic: GA on 70% budget, polish with the rest
    sseed_m = solver_seed_for(seed, f"budget_mem_{budget_s}")
    t0 = time.perf_counter()
    solve_tsp_genetic(cities, population_size=pop_size, generations=5,
                      mutation_rate=0.05, seed=sseed_m)
    per_gen_m = (time.perf_counter() - t0) / 5.0
    gens_m = max(5, int(budget_s * 0.65 / max(per_gen_m, 1e-6)))
    t0 = time.perf_counter()
    m_route, m_dist, _ = solve_tsp_memetic(
        cities, population_size=pop_size, generations=gens_m,
        mutation_rate=0.05, seed=sseed_m)
    cands.append(("memetic", m_route, m_dist,
                  (time.perf_counter() - t0) * 1000.0, sseed_m))

    # 3. Multi-start 2-opt: restart until the budget is spent
    sseed_t = solver_seed_for(seed, f"budget_2opt_{budget_s}")
    rng = _random.Random(sseed_t)
    t0 = time.perf_counter()
    best_r, best_d, starts = None, float("inf"), 0
    while True:
        r = create_random_route(n_cities, rng)
        r, d, _ = two_opt_improve(cities, r)
        starts += 1
        if d < best_d:
            best_r, best_d = r, d
        if time.perf_counter() - t0 >= budget_s:
            break
    cands.append((f"two_opt", best_r, best_d,
                  (time.perf_counter() - t0) * 1000.0, sseed_t))

    ref = min(d for _, _, d, _, _ in cands)
    return [{
        "algorithm": algo,
        "n_cities": n_cities,
        "seed": seed,
        "solver_seed": ss,
        "budget_s": budget_s,
        "restarts_or_gens": starts if algo == "two_opt" else (
            gens_fit if algo == "pure_ga" else gens_m),
        "distance": float(d),
        "time_ms": float(t),
        "gap_vs_best": float(optimality_gap(d, ref)),
        "route": "-".join(map(str, r)),
    } for algo, r, d, t, ss in cands]


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
    parser.add_argument("--budget", action="store_true",
                        help="Fair-budget mode: equal wall-clock per method "
                             "(sizes 30/50, budgets 2s/10s)")
    parser.add_argument("--out", type=str, default="results/benchmark_results.csv")
    args = parser.parse_args()

    budgets: list = []
    runner = None
    budget_mode = False

    if args.budget:
        budgets = [2.0, 10.0]
        sizes = [30, 50]
        out = args.out if args.out != "results/benchmark_results.csv" \
            else "results/benchmark_budget.csv"
        group_col = "gap_vs_best"
        budget_mode = True
    elif args.scale:
        sizes = [10, 20, 30, 40, 50]
        ga_params = dict(population_size=60, generations=120,
                         mutation_rate=0.05)
        runner = lambda n, s: run_scale_single(n, s, ga_params)
        out = args.out if args.out != "results/benchmark_results.csv" \
            else "results/benchmark_scale.csv"
        group_col = "gap_vs_best"
        budget_mode = False
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
        budget_mode = False

    all_records = []
    if budget_mode:
        total = args.trials * len(sizes) * len(budgets)
        done = 0
        for n in sizes:
            for b in budgets:
                for t in range(args.trials):
                    seed = 1000 + t * 100 + n
                    all_records.extend(run_budget_single(n, seed, b))
                    done += 1
                    print(f"[{done}/{total}] n={n} budget={b}s "
                          f"seed={seed} done")
    else:
        total = args.trials * len(sizes)
        done = 0
    assert runner is not None or budget_mode
    for n in sizes:
        for t in range(args.trials):
            if budget_mode:
                continue  # already ran above
            seed = 1000 + t * 100 + n
            assert runner is not None
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

    if budget_mode:
        # Paired stats: mean / median / std / 95% CI + win counts.
        # Paired because every method saw the SAME maps.
        import numpy as np
        keys = ["algorithm", "n_cities", "budget_s"]
        g = df.groupby(keys)[group_col]
        stats = g.agg(["mean", "median", "std", "count"]).assign(
            ci95=lambda s: 1.96 * s["std"] / np.sqrt(s["count"]))
        print("\nPaired stats (mean | median | std | 95% CI):")
        print(stats.round(2).to_string())
        print("\nPaired wins (maps where method was strictly best):")
        win = df.loc[df.groupby(["n_cities", "budget_s", "seed"])
                     [group_col].idxmin()]
        print(pd.crosstab([win["n_cities"], win["budget_s"]],
                          win["algorithm"]).to_string())


if __name__ == "__main__":
    main()
