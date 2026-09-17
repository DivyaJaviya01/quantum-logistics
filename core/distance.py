"""Distance calculations for TSP routes."""

import numpy as np


def calculate_distance(cities, route):
    """Calculate total distance of a route (list of city indices).

    Args:
        cities: numpy array of shape (n, 2) with city coordinates.
        route: list of city indices representing the route.

    Returns:
        Total Euclidean distance of the route (including return to start).
    """
    total = 0.0
    for i in range(len(route)):
        a = cities[route[i]]
        b = cities[route[(i + 1) % len(route)]]
        total += np.linalg.norm(a - b)
    return total
