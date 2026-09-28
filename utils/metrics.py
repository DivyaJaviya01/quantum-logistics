"""Research metrics for TSP solver comparison."""

import numpy as np


def optimality_gap(found_distance, optimal_distance):
    """Compute % gap from optimal: (found - optimal) / optimal * 100."""
    if optimal_distance == 0:
        return 0.0
    return (found_distance - optimal_distance) / optimal_distance * 100.0


def success_rate(gaps, tolerance=1.0):
    """Fraction of runs within tolerance % of optimal."""
    gaps = np.asarray(gaps)
    return float(np.mean(gaps <= tolerance))


def distance_matrix(cities):
    """Full pairwise Euclidean distance matrix (n x n)."""
    n = len(cities)
    mat = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            mat[i, j] = np.linalg.norm(cities[i] - cities[j])
    return mat


def route_leg_distances(cities, route):
    """Per-leg distances for a route (including return to start)."""
    legs = []
    for i in range(len(route)):
        a = cities[route[i]]
        b = cities[route[(i + 1) % len(route)]]
        legs.append(float(np.linalg.norm(a - b)))
    return legs


def summarize_runs(records):
    """Summarize a list of dict records into mean/std stats per group.

    Args:
        records: list of dicts with keys e.g. algorithm, n_cities, distance, time_ms, gap.

    Returns:
        pandas DataFrame grouped by (algorithm, n_cities) with mean/std.
    """
    import pandas as pd
    df = pd.DataFrame(records)
    grouped = df.groupby(["algorithm", "n_cities"]).agg(
        mean_distance=("distance", "mean"),
        std_distance=("distance", "std"),
        mean_time_ms=("time_ms", "mean"),
        std_time_ms=("time_ms", "std"),
        mean_gap=("gap", "mean"),
        success_1pct=("gap", lambda s: float((s <= 1.0).mean())),
        runs=("distance", "count"),
    ).reset_index()
    return grouped
