# 02 — The 5 Solvers (Our Racers)

All 5 take city positions in, and give (best route, route length) out.
Same input, same output — so the race is fair.

---

## Racer 1: Brute-Force — "the keychain checker"

**Method:** list every possible order, measure each, keep the shortest.

**Analogy:** you lost your key and try every key on the keychain one by one.
With 5 keys it is instant. With 1 lakh keys you die trying.

**Strengths:** always 100% perfect (the *definition* of optimal).
**Weakness:** factorial explosion — refused above 10 cities in our code.
**File:** `algorithms/tsp_bruteforce.py` → `solve_tsp_bruteforce(cities)`
**Role in project:** the judge. It tells us the true answer on small maps,
so we can grade everyone else.

---

## Racer 2: Genetic Algorithm (GA) — "the horse breeder"

**Method (repeated for ~100 generations):**
1. Make 50 random routes (**population** — each route is an **individual**).
2. Score each: shorter route = higher **fitness** (`fitness = 1 / distance`).
3. Pick winners by mini-contests (**tournament selection**).
4. Mix two winners into a child route (**Order Crossover (OX)** — copies a
   segment from one parent, fills the rest from the other *without repeating
   any city*, because a repeated city = an invalid route).
5. Rarely swap two cities at random (**mutation**, ~5%) to stay creative.
6. Always keep the best route safe (**elitism** — never lose the champion).

**Analogy:** breeding racehorses. Fast parents → baby horse → hopefully
faster. Repeat 100 generations.

**Strengths:** fast, needs no map knowledge, great on small maps.
**Weakness:** at 40–50 cities it leaves tangled, crossed roads everywhere —
measured **106% worse than best** at N=50 (file 06). Evolution explores
well but fine-tunes badly.
**File:** `algorithms/genetic_algorithm.py` → `solve_tsp_genetic(...)`
returns `(route, distance, history)` — history = best distance per
generation, used to draw learning curves.

---

## Racer 3: 2-opt — "the wire straightener"

**Method:** look at the route. If two roads cross like an **X**, uncross them
into **||** (reverse the cities between the two crossing points). Uncrossing
*always* shortens the route. Repeat until no crossing pair improves anything
(a **local optimum**). Each check costs O(1) thanks to **delta evaluation**:
a swap only changes 2 roads, so we compare just those instead of
re-measuring the whole route (~1000× faster).

**Analogy:** your earphone wire is tangled. You don't buy new earphones —
you untangle what you have, knot by knot, until smooth.

**Strengths:** tiny, fast (85 ms for 50 cities), optimal polisher.
**Weakness:** can only polish the route it is given; a bad start can trap it
in a mediocre tangle. Fix: restart from many random routes…
**File:** `algorithms/two_opt.py` → `two_opt_improve(cities, route)`

---

## Racer 4: Memetic (GA + 2-opt) — "coach + player"

**Method:** run the full Genetic Algorithm, then hand its champion to 2-opt
for final polishing. (Optional strong mode: polish the champion every K
generations so improvements re-enter the gene pool — called **Lamarckian**
learning, after the idea that练 acquired traits can be inherited.)

**Analogy:** the horse breeder (GA) finds a fast horse; then a professional
trainer (2-opt) fixes its running posture. Team beats either alone.

**Strengths:** stays within 0–8% of best-found at ALL sizes 10–50.
**Weakness:** still loses to plain multi-start 2-opt on our maps (file 06).
**File:** `algorithms/memetic.py` → `solve_tsp_memetic(...)`

---

## Racer 5: QAOA — "the quantum dreamer"

**Method (real, not fake):**
1. Translate the map into a quantum puzzle (**QUBO**: each "city i at
   position p" becomes a qubit; short tours = low energy).
   Trick: the shop is fixed, so only (N−1)² qubits are needed (16 for
   5 cities instead of 25).
2. Build a quantum circuit with `p` layers (cost layer + mixer layer) and
   simulate it on our laptop (**statevector**: 2¹⁶ = 65,536 numbers).
3. Tune the circuit's angles with a classical optimizer (**COBYLA**) to
   push the average energy down.
4. Read the most likely answers, convert bitstrings back to routes
   (repairing conflicts), keep the shortest real route.

**Analogy:** instead of walking roads, dream all roads at once (quantum
superposition), then wake up holding the shortest one.

**Strengths:** found the EXACT optimum at N=4 and N=5. Fully free tools
(NumPy + SciPy, no Qiskit, no paid service).
**Weaknesses:**
- Simulation memory doubles per qubit → hard cap at **N ≤ 5**
  (N=6 needs 33 million numbers). Bigger maps need real quantum hardware.
- The optimizer can get stuck in a **local minimum** (measured: 17% gap on
  one map with too few iterations — honest quantum behaviour).
**File:** `algorithms/qaoa.py` → `solve_tsp_qaoa(...)`

---

## Cheat sheet

| Racer | Type | Guarantee | Needs quantum? | Max map in our code |
|---|---|---|---|---|
| Brute-Force | exact | 100% optimal | no | 10 cities |
| Genetic Alg. | heuristic | none | no | unlimited (degrades) |
| 2-opt x20 | heuristic | none | no | unlimited (our champion) |
| Memetic | hybrid heuristic | none | no | unlimited |
| QAOA | quantum heuristic | none | simulated only (≤5) | 5 cities |
