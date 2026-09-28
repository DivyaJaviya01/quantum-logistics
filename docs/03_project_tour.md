# 03 — Project Tour (Every Folder and File)

```
quantum-logistics/
├── main.py                  ← front door: starts the website
├── PROJECT_GUIDE.md         ← short story version of these docs
├── README.md                ← short intro + run instructions
├── PROBLEM_STATEMENT.md     ← research specification
├── PHASE_REPORT.md          ← what was built in which phase
│
├── algorithms/              ← the 5 racers (file 02)
│   ├── tsp_bruteforce.py    ← Racer 1
│   ├── genetic_algorithm.py ← Racer 2
│   ├── two_opt.py           ← Racer 3 (+ polishing tool)
│   ├── memetic.py           ← Racer 4
│   └── qaoa.py              ← Racer 5
│
├── core/                    ← shared kitchen (all racers eat here, so fair)
│   ├── city_generator.py    ← generate_cities(n, seed): random map maker
│   └── distance.py          ← calculate_distance(cities, route): measuring tape
│
├── ui/                      ← drawing rooms (what you SEE; never solve anything)
│   ├── streamlit_app.py     ← fancy website (buttons, sliders, maps, charts)
│   └── app.py               ← simple desktop window (Tkinter)
│
├── utils/                   ← toolbox
│   ├── plotting.py          ← plot_cities(), plot_route(): paintbrushes
│   └── metrics.py           ← optimality_gap(), distance_matrix(): scorecards
│
├── experiments/             ← science lab (fair races, writes scores to CSV)
│   └── benchmark.py         ← the race organizer (small-N mode + --scale mode)
│
├── notebooks/               ← photo albums with charts (files 04–05 explain each)
│   ├── 01_tsp_research_analysis.ipynb (+ _executed with pictures)
│   └── 02_scale_up_memetic.ipynb       (+ _executed with pictures)
│
├── results/                 ← marksheet drawer (CSVs)
│   ├── benchmark_results.csv      ← 120 rows: small-N race (BF + GA)
│   ├── benchmark_qaoa_check.csv  ← 18 rows: QAOA spot-checks
│   └── benchmark_scale.csv       ← 75 rows: big-N race (3 methods × 5 sizes × 5 maps)
│
├── docs/                    ← you are here (full explanation)
├── test_ga.py               ← health checkup: is the GA healthy?
├── test_qaoa.py             ← health checkup: is QAOA healthy?
├── test_memetic.py          ← health checkup: GA vs Memetic at 10–50 cities
└── requirements.txt         ← shopping list: pip install -r requirements.txt
```

## How one button-click travels through the project

```
You click "Solve TSP" in the browser
        │  ui/streamlit_app.py receives the click
        ▼  (calls the racer you picked)
algorithms/memetic.py runs GA, then polishes with 2-opt
        │  (asks the kitchen to measure every candidate)
        ▼
core/distance.py returns lengths
        │  (best route goes back to the drawing room)
        ▼
utils/plotting.py draws the blue route on the map
        │  (utils/metrics.py computes the score)
        ▼
You see map + "Distance: 475.20" + convergence chart
```

**Golden rule: nobody does another person's job.** The UI never solves,
the solver never draws, the kitchen never decides. That is why adding a
6th racer later means adding ONE file in `algorithms/` and nothing else.
