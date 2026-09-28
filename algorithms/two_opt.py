"""2-opt local search for TSP.

Idea in one line: if two roads cross like an 'X', uncross them into '||'.
Uncrossing always shortens the route. Repeat until nothing crosses.

Works on any route, needs no quantum computer, runs in milliseconds.
This is the classic trick that fixes GA's weakness at large N.
"""

import numpy as np


def two_opt_swap(route, i, k):
    """Reverse the segment between positions i and k.

    Example: [0,1,2,3,4,5] with i=2,k=4 -> [0,1,4,3,2,5]
    Reversing = uncrossing the two roads at the segment ends.
    """
    return route[:i] + route[i:k + 1][::-1] + route[k + 1:]


def two_opt_improve(cities, route, max_passes=None):
    """Polish a route with 2-opt until no improvement (local optimum).

    One pass = scan all swaps, apply the first improvement, restart.
    Stops when a full pass finds nothing (true local optimum).

    Args:
        cities: numpy array of shape (N, 2).
        route: list of city indices, starts at 0.
        max_passes: safety cap on passes. Defaults to 20 * N.

    Returns:
        Tuple (best_route, best_distance, passes_used).
    """
    from core.distance import calculate_distance

    n = len(route)
    if max_passes is None:
        max_passes = 20 * n
    best = list(route)

    # Precompute distance matrix once (indexed by CITY id); a 2-opt swap
    # only changes 2 edges, so each candidate is evaluated in O(1) via
    # delta instead of an O(N) full re-sum.
    m = len(cities)
    C = np.zeros((m, m))
    for a in range(m):
        for b in range(m):
            C[a, b] = float(np.linalg.norm(cities[a] - cities[b]))

    def tour_len(r):
        return float(sum(C[r[i], r[(i + 1) % n]] for i in range(n)))

    best_dist = tour_len(best)

    passes = 0
    while passes < max_passes:
        passes += 1
        improved = False
        # Try every pair (i, k); keep first improvement, restart scan
        for i in range(1, n - 1):
            for k in range(i + 1, n):
                a, b = best[i - 1], best[i]
                c, d_ = best[k], best[(k + 1) % n]
                delta = (C[a, c] + C[b, d_]) - (C[a, b] + C[c, d_])
                if delta < -1e-9:
                    best = two_opt_swap(best, i, k)
                    best_dist += delta
                    improved = True
                    break
            if improved:
                break
        if not improved:
            break
    return best, best_dist, passes


def count_crossings(cities, route):
    """Count crossing road pairs (diagnostic: shows why 2-opt helps)."""
    def _cross(p1, p2, p3, p4):
        # Do segments p1-p2 and p3-p4 cross? (orientation test)
        def orient(a, b, c):
            return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
        d1 = orient(p3, p4, p1)
        d2 = orient(p3, p4, p2)
        d3 = orient(p1, p2, p3)
        d4 = orient(p1, p2, p4)
        return ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0))

    pts = [cities[r] for r in route] + [cities[route[0]]]
    m = len(route)
    crossings = 0
    for i in range(m):
        for j in range(i + 2, m):
            if i == 0 and j == m - 1:
                continue  # adjacent (share depot), skip
            if _cross(pts[i], pts[i + 1], pts[j], pts[(j + 1) % m]):
                crossings += 1
    return int(crossings)
