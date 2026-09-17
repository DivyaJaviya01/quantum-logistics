"""City generation for TSP."""

import numpy as np


def generate_cities(n=5, seed=None):
    """Generate n cities with random x, y coordinates in [0, 100].

    Args:
        n: Number of cities to generate.
        seed: Random seed for reproducibility.

    Returns:
        numpy array of shape (n, 2) with city coordinates.
    """
    if seed is not None:
        np.random.seed(seed)
    cities = np.random.rand(n, 2) * 100
    return cities
