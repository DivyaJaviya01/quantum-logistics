"""Plotting utilities for TSP visualization."""

import matplotlib.pyplot as plt


def plot_cities(ax, cities):
    """Plot cities on a matplotlib axis.

    Args:
        ax: matplotlib axis to draw on.
        cities: numpy array of shape (n, 2) with city coordinates.
    """
    ax.clear()
    ax.set_title("Cities")
    ax.scatter(cities[:, 0], cities[:, 1], c='red', s=80, zorder=5)
    for i, (x, y) in enumerate(cities):
        ax.annotate(f"City {i+1}", (x, y), textcoords="offset points", xytext=(5, 5))
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.grid(True, alpha=0.3)


def plot_route(ax, cities, route):
    """Plot a TSP route on a matplotlib axis.

    Args:
        ax: matplotlib axis to draw on.
        cities: numpy array of shape (n, 2) with city coordinates.
        route: list of city indices representing the route.
    """
    ax.clear()
    ax.set_title("Optimal Route")

    # Draw route lines
    route_coords = cities[route + [route[0]]]
    ax.plot(route_coords[:, 0], route_coords[:, 1], 'b-', linewidth=1.5, alpha=0.7)

    # Draw cities
    ax.scatter(cities[:, 0], cities[:, 1], c='red', s=80, zorder=5)
    for i, (x, y) in enumerate(cities):
        ax.annotate(f"City {i+1}", (x, y), textcoords="offset points", xytext=(5, 5))

    # Mark start city
    start = cities[0]
    ax.scatter([start[0]], [start[1]], c='green', s=120, zorder=6, label='Start (City 1)')
    ax.legend()

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.grid(True, alpha=0.3)
