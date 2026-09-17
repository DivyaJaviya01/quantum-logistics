"""Brute-force TSP solver."""

from itertools import permutations
from core.distance import calculate_distance


def solve_tsp_bruteforce(cities):
    """Brute-force solver: check all permutations, return shortest route.

    Fixes City 1 (index 0) as start, permutes all other cities,
    and returns the route with minimum total distance.

    Args:
        cities: numpy array of shape (n, 2) with city coordinates.

    Returns:
        Tuple of (best_route, best_distance) where best_route is a list
        of city indices and best_distance is a float.
    """
    n = len(cities)
    other_cities = list(range(1, n))
    best_distance = float('inf')
    best_route = None

    for perm in permutations(other_cities):
        route = [0] + list(perm)
        dist = calculate_distance(cities, route)
        if dist < best_distance:
            best_distance = dist
            best_route = route

    return best_route, best_distance
