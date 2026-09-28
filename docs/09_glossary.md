# 09 — Glossary (Dictionary)

| Word | Simple meaning | Where met |
|---|---|---|
| TSP | Delivery-route problem: visit all once, return, shortest path | file 01 |
| City | One delivery point (x, y on the map) | file 01 |
| Depot | The shop / City 1; fixed start and end | file 01 |
| Route / tour | One full visiting order + return | file 01 |
| Optimal | The shortest possible (only known for small maps) | file 01 |
| Gap % | % longer than the reference answer; 0% = matched it | file 01 |
| Heuristic | Smart shortcut: fast, usually good, never guaranteed | file 01 |
| Brute-force | Checking every possible order | file 02 |
| Factorial (!) | 5! = 5×4×3×2×1; grows explosively; why BF dies | file 01 |
| Population | GA's set of candidate routes (e.g. 50) | file 02 |
| Individual / chromosome | One route inside the population | file 02 |
| Fitness | Score: `1 / distance` (shorter = fitter) | file 02 |
| Tournament selection | Mini-contest: best of 3 random routes becomes parent | file 02 |
| Crossover (OX) | Mix two parent routes without repeating cities | file 02 |
| Mutation | Rare random swap to stay creative (~5%) | file 02 |
| Elitism | Never throw away the champion | file 02 |
| Generation | One evolve cycle; our GA runs 100–200 | file 02 |
| 2-opt | Uncross two roads; repeat till nothing improves | file 02 |
| Local optimum | Answer no small change can improve (maybe not global best) | file 02 |
| Local minimum | Same idea for energy/cost (QAOA trap) | file 02 |
| Delta evaluation | Judge a swap by its 2 changed roads only (O(1)) | file 02 |
| Memetic | GA explores + 2-opt polishes (hybrid) | file 02 |
| Lamarckian | Polished improvements re-enter the gene pool | file 02 |
| QAOA | Quantum method: encode → quantum circuit → tune → sample | file 02 |
| QUBO | Quantum-friendly puzzle form (0/1 variables, penalties) | file 02 |
| Qubit | Quantum bit; our TSP needs (N−1)² of them | file 02 |
| Statevector | Full list of quantum probabilities (2^qubits numbers) | file 02 |
| COBYLA | Classical tuner for QAOA's angles (no gradients needed) | file 02 |
| gap_vs_best | Gap vs best-found (big maps, optimum unknown) | file 05 |
| Convergence | Learning curve flattening = method stopped improving | file 04 |
| Significance | Statistical proof a win isn't luck (we don't have this yet) | file 07 |
