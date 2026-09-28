"""QAOA TSP solver (simulated with NumPy + SciPy).

Real Quantum Approximate Optimization Algorithm, simulated classically:
  1. Map TSP to a QUBO (depot City 1 fixed at position 0 -> only (N-1)^2 qubits).
  2. Build the cost Hamiltonian (diagonal: energy of every bitstring).
  3. Run the QAOA circuit (cost + mixer layers) as a statevector simulation.
  4. Optimize angles (gamma, beta) with COBYLA to minimize <H_C>.
  5. Sample the final state, decode bitstrings to routes, keep the shortest.

Free tools only: numpy + scipy. No Qiskit / no paid API needed.

Limit: exact simulation needs 2^((N-1)^2) amplitudes,
so N <= 5 cities (16 qubits). Larger N raises a clear error.
"""

import numpy as np

from core.distance import calculate_distance

MAX_CITIES_EXACT = 5


# ---------------------------------------------------------------------------
# QUBO formulation (depot fixed)
# ---------------------------------------------------------------------------

def build_qubo_energies(cities, penalty=None):
    """Precompute the QUBO energy of every possible bitstring.

    Variables: x[i,p] = 1 if city i (1..N-1) is visited at position p (1..N-1).
    City 0 (depot) is fixed at position 0 and at the end.

    Energy = tour cost + penalty * (constraint violations), where constraints
    are "one city per position" and "each city visited once".

    Args:
        cities: numpy array of shape (N, 2).
        penalty: weight for constraint violations. Defaults to N * max distance.

    Returns:
        Tuple (energies, n_qubits) where energies[k] is the energy of the
        bitstring representing integer k.
    """
    n = len(cities)
    m = n - 1  # cities excluding depot
    n_qubits = m * m

    # Pairwise distances
    dist = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            dist[i, j] = np.linalg.norm(cities[i] - cities[j])

    if penalty is None:
        penalty = float(n * dist.max())

    # Bit matrix: rows = all 2^n_qubits bitstrings, cols = qubits.
    # Qubit q corresponds to city i = q % m + 1, position p = q // m + 1.
    size = 1 << n_qubits
    ints = np.arange(size, dtype=np.int64)[:, None]
    shifts = np.arange(n_qubits, dtype=np.int64)[None, :]
    bits = ((ints >> shifts) & 1).astype(float)  # (size, n_qubits)

    # Reshape to X[k, i, p] with i, p in 0..m-1 (= city i+1, position p+1)
    X = bits.reshape(size, m, m).transpose(0, 2, 1)  # X[k, pos, city]

    # --- Tour cost ---
    # First leg: depot -> position 1
    cost = (X[:, 0, :] * dist[0, 1:]).sum(axis=1)
    # Middle legs: position p -> p+1
    for p in range(m - 1):
        cost = cost + np.einsum("ki,kj,ij->k", X[:, p, :], X[:, p + 1, :], dist[1:, 1:])
    # Last leg: position m -> depot
    cost = cost + (X[:, m - 1, :] * dist[1:, 0]).sum(axis=1)

    # --- Constraint penalties ---
    row_err = (X.sum(axis=2) - 1.0) ** 2   # one city per position
    col_err = (X.sum(axis=1) - 1.0) ** 2   # each city visited once
    energies = cost + penalty * (row_err.sum(axis=1) + col_err.sum(axis=1))

    return energies, n_qubits


# ---------------------------------------------------------------------------
# Statevector QAOA simulation
# ---------------------------------------------------------------------------

def _apply_mixer(state, beta, n_qubits):
    """Apply exp(-i * beta * sum(X)) = RX(2*beta) on every qubit, in place."""
    cos_b = np.cos(beta)
    sin_b = np.sin(beta)
    size = state.shape[0]
    for q in range(n_qubits):
        step = 1 << q
        # Pairs of amplitudes differing only in qubit q
        s = state.reshape(-1, 2 * step)
        a = s[:, :step].copy()
        b = s[:, step:].copy()
        s[:, :step] = cos_b * a - 1j * sin_b * b
        s[:, step:] = -1j * sin_b * a + cos_b * b
    assert state.shape[0] == size


def qaoa_expectation(params, energies, n_qubits, depth):
    """Run the QAOA circuit and return <H_C> (mean energy)."""
    gammas = params[:depth]
    betas = params[depth:]
    size = 1 << n_qubits
    state = np.full(size, 1.0 / np.sqrt(size), dtype=complex)  # |+>^n
    for layer in range(depth):
        state = state * np.exp(-1j * gammas[layer] * energies)  # cost unitary
        _apply_mixer(state, betas[layer], n_qubits)             # mixer unitary
    probs = np.abs(state) ** 2
    return float(np.dot(probs, energies))


def qaoa_final_state(params, energies, n_qubits, depth):
    """Run the QAOA circuit and return the final statevector."""
    gammas = params[:depth]
    betas = params[depth:]
    size = 1 << n_qubits
    state = np.full(size, 1.0 / np.sqrt(size), dtype=complex)
    for layer in range(depth):
        state = state * np.exp(-1j * gammas[layer] * energies)
        _apply_mixer(state, betas[layer], n_qubits)
    return state


# ---------------------------------------------------------------------------
# Decode bitstrings -> valid TSP routes
# ---------------------------------------------------------------------------

def decode_bitstring(k, n):
    """Decode integer bitstring k into a route, repairing conflicts.

    For each position picks the city flagged with 1; if none/multiple or the
    city is already used, falls back to the first unused city. Always returns
    a valid route starting at city 0.
    """
    m = n - 1
    used = set()
    route = [0]
    for p in range(1, n):
        chosen = None
        for i in range(1, n):
            q = (p - 1) * m + (i - 1)
            if (k >> q) & 1 and i not in used:
                chosen = i
                break
        if chosen is None:  # conflict or empty -> first unused city
            for i in range(1, n):
                if i not in used:
                    chosen = i
                    break
        assert chosen is not None  # always one unused city left
        route.append(chosen)
        used.add(chosen)
    return route


# ---------------------------------------------------------------------------
# Main solver
# ---------------------------------------------------------------------------

def solve_tsp_qaoa(cities, depth=2, penalty=None, maxiter=80, seed=42,
                   top_k=20):
    """Solve TSP with QAOA (classical statevector simulation).

    Args:
        cities: numpy array of shape (N, 2). N must be <= 5 for exact sim.
        depth: QAOA layers p (more layers = better, but slower).
        penalty: QUBO constraint weight. Defaults to N * max distance.
        maxiter: COBYLA optimizer iterations.
        seed: random seed for initial angles.
        top_k: number of most-probable bitstrings to decode as candidates.

    Returns:
        Tuple (best_route, best_distance, info) where info holds
        qubits, depth, final expectation, optimizer history, and penalty.
    """
    n = len(cities)
    if n > MAX_CITIES_EXACT:
        raise ValueError(
            f"Exact QAOA simulation supports N <= {MAX_CITIES_EXACT} cities "
            f"({(MAX_CITIES_EXACT - 1) ** 2} qubits), got N={n} "
            f"({(n - 1) ** 2} qubits = {2 ** ((n - 1) ** 2):,} amplitudes). "
            "Reduce the number of cities."
        )

    from scipy.optimize import minimize

    energies, n_qubits = build_qubo_energies(cities, penalty)

    rng = np.random.default_rng(seed)
    x0 = rng.uniform(0, 2 * np.pi, size=2 * depth)

    history = []
    result = minimize(
        lambda p: qaoa_expectation(p, energies, n_qubits, depth),
        x0, method="COBYLA",
        options={"maxiter": maxiter, "disp": False},
        callback=lambda p: history.append(
            qaoa_expectation(p, energies, n_qubits, depth)),
    )
    history.append(float(result.fun))

    # Sample final state: decode top-K bitstrings, keep shortest true route
    state = qaoa_final_state(result.x, energies, n_qubits, depth)
    probs = np.abs(state) ** 2
    top = np.argsort(probs)[::-1][:top_k]

    best_route, best_dist = None, float("inf")
    for k in top:
        route = decode_bitstring(int(k), n)
        d = calculate_distance(cities, route)
        if d < best_dist:
            best_dist, best_route = d, route

    info = {
        "qubits": n_qubits,
        "depth": depth,
        "penalty": float(penalty) if penalty is not None else float(n * np.max(
            [np.linalg.norm(cities[i] - cities[j])
             for i in range(n) for j in range(n)])),
        "expectation": float(result.fun),
        "history": history,
        "top_prob": float(probs[top[0]]),
    }
    return best_route, best_dist, info
