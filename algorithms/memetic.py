"""Memetic solver: Genetic Algorithm + 2-opt local search.

Why: pure GA is good at exploring (finds promising areas) but bad at
fine-tuning (leaves small crossings in the route). 2-opt is the opposite:
great at polishing one route, but stuck with whatever it is given.
Together: GA explores, 2-opt polishes. Standard hybrid, big quality jump
at large N, still zero quantum hardware.
"""

from core.distance import calculate_distance
from algorithms.genetic_algorithm import solve_tsp_genetic
from algorithms.two_opt import two_opt_improve


def solve_tsp_memetic(cities, population_size=100, generations=200,
                      mutation_rate=0.05, polish_every=0):
    """Solve TSP with GA, then polish the winner with 2-opt.

    Args:
        cities: numpy array of shape (N, 2).
        population_size, generations, mutation_rate: GA settings.
        polish_every: if > 0, also 2-opt-polish the elite every K
            generations (slower but stronger). 0 = polish only at the end.

    Returns:
        Tuple (best_route, best_distance, info) where info holds
        ga_distance (before polish), sweeps_used, and ga history.
    """
    from algorithms.genetic_algorithm import (
        create_initial_population, evaluate_population,
        tournament_selection, order_crossover, swap_mutation,
        is_valid_route,
    )

    n = len(cities)

    if polish_every <= 0:
        # Simple mode: full GA run, then one 2-opt polish at the end
        ga_route, ga_dist, history = solve_tsp_genetic(
            cities, population_size=population_size,
            generations=generations, mutation_rate=mutation_rate)
        best_route, best_dist, sweeps = two_opt_improve(cities, ga_route)
    else:
        # Strong mode: polish the elite every K generations (Lamarckian:
        # the polished route re-enters the population)
        population = create_initial_population(n, population_size)
        best_ever_route, best_ever_distance = None, float("inf")
        history = []
        for gen in range(generations):
            scored = evaluate_population(population, cities)
            gen_best_route = list(scored[0][0])
            if polish_every and (gen + 1) % polish_every == 0:
                gen_best_route, _, _ = two_opt_improve(cities, gen_best_route)
            gen_best_dist = calculate_distance(cities, gen_best_route)
            if gen_best_dist < best_ever_distance:
                best_ever_distance = gen_best_dist
                best_ever_route = list(gen_best_route)
            history.append(best_ever_distance)
            new_population = [list(gen_best_route)]
            while len(new_population) < population_size:
                p1 = tournament_selection(scored)
                p2 = tournament_selection(scored)
                child = swap_mutation(
                    order_crossover(p1, p2), mutation_rate)
                if is_valid_route(child, n):
                    new_population.append(child)
            population = new_population
        ga_route, ga_dist = best_ever_route, best_ever_distance
        best_route, best_dist, sweeps = two_opt_improve(cities, ga_route)

    info = {
        "ga_distance": float(ga_dist),
        "polish_gain": float(ga_dist - best_dist),
        "sweeps_used": sweeps,
        "history": history,
    }
    return best_route, best_dist, info
