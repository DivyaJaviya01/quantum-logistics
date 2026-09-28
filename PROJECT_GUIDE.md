# Quantum Logistics — Whole Project Explained in Simple Words

Think of this project like a **food delivery company**.

You have 5 houses to deliver food to. You start from your shop (City 1),
visit every house exactly once, and come back to the shop.
There are many possible paths. Which path is the shortest?
That question is the **Travelling Salesman Problem (TSP)**.

This project tries **3 different ways** to find the shortest path,
then compares them like a science experiment.

---

## 1. The 3 Solvers (3 Different Delivery Boys)

### Boy 1: Brute-Force (the hardworking boy)
He tries **every possible path** one by one and picks the shortest.
For 5 houses there are only 24 paths, so he is fast and always perfect.

**Problem:** for 10 houses there are 362,880 paths. For 12 houses, lakhs.
He gets tired and slow. He cannot handle big cities.

> Analogy: like checking every key on a keychain one by one. Works if you
> have 5 keys. Impossible if you have 1 lakh keys.

### Boy 2: Genetic Algorithm (the smart learner)
He does NOT check every path. Instead:
1. He makes 50 random paths (population).
2. He keeps the short ones, throws away the long ones (selection).
3. He mixes two good paths to make a new path (crossover).
4. Sometimes he randomly swaps two houses (mutation) so he does not get stuck.
5. He repeats this 100 times (generations). Paths keep getting shorter.

> Analogy: like breeding fast horses. Take two fast horses, make a baby
> horse, hope the baby is faster. Repeat for many generations.

### Boy 4: Memetic (the coach + player team)
Genetic Algorithm finds a good path, then 2-opt polish removes all
crossed roads. Two skills in one boy. Our champion at 40–50 houses.

### Boy 5: Multi-start 2-opt (the persistent trier)
Makes 20 random paths, polishes each one, keeps the best.
Shockingly, he beat everyone in our tests. Simple + stubborn = winner.

### Boy 3: QAOA (the quantum boy)
He turns the map into a **quantum puzzle** (called QUBO), then uses
quantum-style math to find the lowest-energy answer, which equals the
shortest path. We simulate his quantum computer on our laptop using
NumPy + SciPy (fully free, no paid service).

**Problem:** simulating quantum needs huge memory.
5 houses = 16 qubits = 65,536 numbers (fine).
6 houses = 25 qubits = 3.3 crore numbers (laptop dies).
So he only works for 5 or fewer houses. Bigger maps need a real
quantum computer.

> Analogy: like dreaming the answer instead of walking every road.
> Powerful dream, but our laptop-brain is too small for big dreams.

---

## 2. Folder Structure (Map of the Project)

```
quantum-logistics/
│
├── main.py                  ← front door of the house
│
├── algorithms/              ← the 3 delivery boys live here
│   ├── tsp_bruteforce.py    ← Boy 1 (checks every path)
│   ├── genetic_algorithm.py ← Boy 2 (learns and improves)
│   ├── two_opt.py           ← the uncrossing trick (polishes any path)
│   ├── memetic.py           ← Boy 4 (GA + 2-opt team)
│   └── qaoa.py              ← Boy 3 (quantum dream)
│
├── core/                    ← kitchen (basic cooking happens here)
│   ├── city_generator.py    ← makes random houses on the map
│   └── distance.py          ← measuring tape (measures path length)
│
├── ui/                      ← drawing room (where guests come)
│   ├── streamlit_app.py     ← website version (browser)
│   └── app.py               ← desktop version (Tkinter window)
│
├── utils/                   ← toolbox (helper tools)
│   ├── plotting.py          ← draws maps and routes
│   └── metrics.py           ← scorecard (how good is the answer?)
│
├── experiments/             ← science lab (fair testing)
│   └── benchmark.py         ← race organizer (runs all boys, writes scores)
│
├── notebooks/               ← photo album + report card
│   ├── 01_tsp_research_analysis.ipynb          ← run this, see all charts
│   └── 01_tsp_research_analysis_executed.ipynb ← already-run version with pictures
│
├── results/                 ← marksheet drawer
│   ├── benchmark_results.csv      ← 120 race scores
│   └── benchmark_qaoa_check.csv  ← QAOA test scores
│
├── test_ga.py               ← quick health check for Boy 2
├── test_qaoa.py             ← quick health check for Boy 3
├── requirements.txt         ← shopping list (which software to install)
├── README.md                ← short intro of the project
└── PROJECT_GUIDE.md         ← this file (full story)
```

---

## 3. What Each Folder Contains (in Detail)

### `main.py` — the front door
When guests arrive, they enter through the front door.
Running `python main.py` starts the website version of the project.
That is all it does — open the door and call the UI.

### `algorithms/` — the 3 delivery boys' room
This is the brain of the project. Each file is one method of finding
the shortest path. All three take the same input (city coordinates)
and give the same output (best path + its length).
Because of this, you can swap boys without changing anything else.

| File | What it does | Simple meaning |
|---|---|---|
| `tsp_bruteforce.py` | `solve_tsp_bruteforce(cities)` checks all paths, returns shortest | Tries every key |
| `genetic_algorithm.py` | `solve_tsp_genetic(cities, ...)` evolves paths over generations | Breeds fast horses |
| `two_opt.py` | `two_opt_improve(cities, route)` uncrosses roads until shortest | Straightens tangled wire |
| `memetic.py` | `solve_tsp_memetic(cities, ...)` runs GA then polishes with 2-opt | Coach + player team |
| `qaoa.py` | `solve_tsp_qaoa(cities, depth=2)` runs quantum simulation | Dreams the answer |

### `core/` — the kitchen
Basic cooking that every delivery boy needs. No boy cooks himself —
everyone eats from the same kitchen, so results are fair.

| File | What it does | Simple meaning |
|---|---|---|
| `city_generator.py` | `generate_cities(n=5)` makes n random houses with x, y positions | Draws the map |
| `distance.py` | `calculate_distance(cities, route)` measures total path length | Measuring tape |

### `ui/` — the drawing room (what you SEE)
Guests never go to the kitchen. They sit in the drawing room and see
pretty maps. The UI files only show things and take button clicks —
they never solve anything themselves. They call the boys in
`algorithms/` to do the solving.

| File | What it does | Simple meaning |
|---|---|---|
| `streamlit_app.py` | Website with buttons, sliders, maps, charts | Fancy drawing room |
| `app.py` | Simple desktop window (Tkinter) | Simple drawing room |

### `utils/` — the toolbox
Helper tools used by many rooms.

| File | What it does | Simple meaning |
|---|---|---|
| `plotting.py` | `plot_cities()` and `plot_route()` draw maps | Paintbrush |
| `metrics.py` | `optimality_gap()` tells how far an answer is from perfect (in %) | Scorecard |

### `experiments/` — the science lab
A fair race organizer. `benchmark.py` makes many random maps,
runs every delivery boy on the SAME maps, notes down time and distance,
and saves everything in a CSV file. This is how we honestly compare.

> Analogy: like a school exam. Same question paper for all students,
> then compare marks. No cheating possible.

### `notebooks/` — the photo album + report card
Jupyter notebook with 8 sections full of charts:
1. Map of 5 houses + distance table picture
2. All 24 paths picture (best, average, worst)
3. GA learning curve (how it improves every generation)
4. Settings test (which population/mutation works best)
5. Speed test (time vs number of houses, log chart)
6. 30-times repeat test (is GA lucky or reliable?)
7. Gallery of best routes on 4 different maps
8. Future plan (why quantum needs N² qubits — bar chart)

The `_executed` file already has all pictures inside. Just open it.

### `results/` — the marksheet drawer
CSV files (Excel-like tables) with all race scores.
`benchmark_results.csv` has 120 rows: every boy, every map size,
every trial, with distance, time, and gap-from-perfect.

### `test_ga.py` and `test_qaoa.py` — health checkups
Small scripts that ask: "Boy 2 / Boy 3, are you healthy?"
They run the solver once and print the answer.
Doctors checkup, nothing more.

### `requirements.txt` — the shopping list
List of free software this project needs
(numpy, matplotlib, pandas, seaborn, streamlit, scipy...).
Install with: `pip install -r requirements.txt`

---

## 4. How the Files Talk to Each Other (Full Journey)

Follow one button click — "Solve TSP" — step by step:

```
You click "Solve TSP" in the browser
        │
        ▼
ui/streamlit_app.py receives the click
        │
        ▼  (calls the chosen boy)
algorithms/genetic_algorithm.py  (example: you picked GA)
        │
        ▼  (asks the kitchen for measurements)
core/distance.py measures each path's length
        │
        ▼  (returns best path to UI)
ui/streamlit_app.py gets (best_route, best_distance)
        │
        ▼  (asks toolbox to draw)
utils/plotting.py draws the map with blue route lines
        │
        ▼
You see the map + "Distance: 227.35" on screen
```

Nobody does another person's job:
- UI never solves. Solver never draws. Kitchen never decides.
This is called **separation of work**, and it is why adding a 4th
delivery boy later is easy — just add one file in `algorithms/`.

---

## 5. How to Run Everything (What YOU Should Do)

### See the pictures (easiest — nothing to run)
Open in VS Code:
```
notebooks/01_tsp_research_analysis_executed.ipynb
```
All charts are already inside.

### Run the charts yourself
```bash
cd quantum-logistics
jupyter lab notebooks/01_tsp_research_analysis.ipynb
```
Click "Run All". Takes 1–2 minutes.

### Open the website
```bash
cd quantum-logistics
python main.py
```
Open http://localhost:8501 in browser.
Pick algorithm → Generate Cities → Solve TSP.

### Health checkups
```bash
cd quantum-logistics
python test_ga.py     # checks Genetic Algorithm
python test_qaoa.py   # checks QAOA
```
Both should say the gap is 0% (perfect answer).

### Run the science race
```bash
cd quantum-logistics
python -m experiments.benchmark --trials 10 --max-cities 9 --quick
```
Scores go to `results/benchmark_results.csv`.

---

## 6. What We Found (Results in Simple Words)

Small maps (brute-force possible, gap vs true optimum):

| Houses | Brute-Force | Genetic Algorithm | QAOA |
|---|---|---|---|
| 4 | Perfect | Perfect | Perfect |
| 5 | Perfect | Perfect | Perfect |
| 6 | Perfect | Perfect | Too big (needs real quantum computer) |
| 7 | Perfect but slow | 0.2% away from perfect | Too big |
| 8–9 | Very slow | 2–5% away, but super fast | Too big |

Big maps, 40–50 houses (no optimum known, gap vs best-found, 5 maps each):

| Houses | Pure GA | Memetic (GA+2-opt) | 2-opt x20 |
|---|---|---|---|
| 20 | 27% worse | ~2% | best every time |
| 30 | 44% worse | ~6% | best every time |
| 40 | 74% worse | ~8% | best every time |
| 50 | 106% worse (2x!) | ~4% | best every time |

Full proof with charts: `notebooks/02_scale_up_memetic_executed.ipynb`.
Raw scores: `results/benchmark_scale.csv` (75 rows).

**Final rule:**
- Small maps (5 or less) → any boy works, all perfect.
- Medium maps (6–9) → use Genetic Algorithm (fast + almost perfect).
- Big maps (10+) → brute-force impossible, GA is your friend, QAOA needs real hardware.

**One honest weak point:** QAOA sometimes gets stuck in a "local minimum"
(a valley that looks lowest but is not the deepest valley).
Giving it more optimizer rounds fixes it. This is real quantum behaviour
and good material for your report.

---

## 7. What Is Left (Future Work)

1. **Real quantum hardware** — run QAOA on an actual quantum computer
   for 6+ houses (our laptop can only dream small dreams).
2. **More houses** — test GA on 20, 50, 100 houses where brute-force
   is fully impossible.
3. **Real city maps** — replace random points with real delivery locations.
4. **New boys** — add Simulated Annealing, Ant Colony, or other solvers
   in `algorithms/`. Just one new file, nothing else changes.

---

*End of guide. If you understand the delivery-boy story, you understand
the whole project.*
