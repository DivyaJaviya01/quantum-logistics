"""Genetic Algorithm TSP solver."""

import random
from core.distance import calculate_distance


def is_valid_route(route, n):
    """Check if a route is a valid TSP permutation.

    A valid route must:
    - Have exactly n cities
    - Start with city 0 (City 1)
    - Contain every city from 0 to n-1 exactly once

    Args:
        route: list of city indices.
        n: total number of cities.

    Returns:
        True if valid, False otherwise.
    """
    if len(route) != n:
        return False
    if route[0] != 0:
        return False
    if sorted(route) != list(range(n)):
        return False
    return True


def create_random_route(n):
    """Create a random valid route starting at city 0.

    Generates a random permutation of cities 1..n-1,
    then prepends city 0 as the fixed starting point.

    Args:
        n: total number of cities.

    Returns:
        A list of city indices representing a valid route.
    """
    route = list(range(1, n))
    random.shuffle(route)
    return [0] + route


def create_initial_population(n, population_size):
    """Generate an initial population of random valid routes.

    Args:
        n: total number of cities.
        population_size: number of routes to generate.

    Returns:
        A list of routes (each route is a list of city indices).
    """
    population = []
    for _ in range(population_size):
        route = create_random_route(n)
        population.append(route)
    return population


def evaluate_population(population, cities):
    """Calculate fitness for each route in the population.

    Fitness = 1 / distance (shorter route = higher fitness).

    Args:
        population: list of routes.
        cities: numpy array of city coordinates.

    Returns:
        List of (route, fitness) tuples, sorted by fitness descending.
    """
    scored = []
    for route in population:
        dist = calculate_distance(cities, route)
        fitness = 1.0 / dist
        scored.append((route, fitness))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored


def tournament_selection(scored_population, tournament_size=3):
    """Select one parent using tournament selection.

    Picks tournament_size random routes from the population,
    the one with highest fitness (shortest distance) wins.

    Args:
        scored_population: list of (route, fitness) tuples.
        tournament_size: number of routes in each tournament.

    Returns:
        The winning route (list of city indices).
    """
    tournament = random.sample(scored_population, tournament_size)
    winner = max(tournament, key=lambda x: x[1])
    return winner[0]


def order_crossover(parent1, parent2):
    """Perform Order Crossover (OX) on two parent routes.

    OX preserves a segment from parent1 and fills remaining
    positions with cities from parent2 in their original order,
    skipping cities already in the child.

    Args:
        parent1: first parent route (list of city indices).
        parent2: second parent route (list of city indices).

    Returns:
        A child route (list of city indices).
    """
    n = len(parent1)
    # Choose two random cut points (start < end)
    start, end = sorted(random.sample(range(n), 2))

    # Step 1: Copy segment from parent1
    child = [None] * n
    child[start:end+1] = parent1[start:end+1]

    # Step 2: Fill remaining positions with cities from parent2
    # in their original order, skipping duplicates
    segment = set(child[start:end+1])
    fill_values = [city for city in parent2 if city not in segment]

    fill_index = 0
    for i in range(n):
        if child[i] is None:
            child[i] = fill_values[fill_index]
            fill_index += 1

    return child


def swap_mutation(route, mutation_rate):
    """Apply swap mutation to a route with given probability.

    With probability mutation_rate, selects two random positions
    and swaps the cities at those positions.

    Args:
        route: list of city indices.
        mutation_rate: probability of mutation (0.0 to 1.0).

    Returns:
        The (possibly mutated) route.
    """
    if random.random() < mutation_rate:
        n = len(route)
        i, j = random.sample(range(1, n), 2)  # skip city 0
        route[i], route[j] = route[j], route[i]
    return route


def solve_tsp_genetic(cities, population_size=50, generations=100, mutation_rate=0.05):
    """Solve TSP using a Genetic Algorithm.

    Uses tournament selection, Order Crossover (OX), swap mutation,
    and elitism to evolve a population of routes toward the optimum.

    Args:
        cities: numpy array of shape (n, 2) with city coordinates.
        population_size: number of routes in the population.
        generations: number of generations to evolve.
        mutation_rate: probability of mutating a child route.

    Returns:
        Tuple of (best_route, best_distance, history) where:
        - best_route: list of city indices for the best route found
        - best_distance: float, total distance of the best route
        - history: list of best distances at each generation
    """
    n = len(cities)

    # Step 1: Create initial population
    population = create_initial_population(n, population_size)

    # Track the best solution overall (elitism)
    best_ever_route = None
    best_ever_distance = float('inf')
    history = []

    for gen in range(generations):
        # Step 2: Evaluate fitness of all routes
        scored = evaluate_population(population, cities)

        # Step 3: Record best in this generation
        gen_best_route = scored[0][0]
        gen_best_dist = 1.0 / scored[0][1]

        # Update overall best
        if gen_best_dist < best_ever_distance:
            best_ever_distance = gen_best_dist
            best_ever_route = list(gen_best_route)

        history.append(best_ever_distance)

        # Step 4: Create next generation
        new_population = []

        # Elitism: keep the best route unchanged
        new_population.append(list(gen_best_route))

        # Fill rest of new population with children
        while len(new_population) < population_size:
            # Select two parents
            parent1 = tournament_selection(scored)
            parent2 = tournament_selection(scored)

            # Crossover to create child
            child = order_crossover(parent1, parent2)

            # Mutation
            child = swap_mutation(child, mutation_rate)

            # Validate child
            if is_valid_route(child, n):
                new_population.append(child)

        population = new_population

    return best_ever_route, best_ever_distance, history
