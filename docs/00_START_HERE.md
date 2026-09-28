# 📚 Quantum Logistics — Full Documentation

**For someone who knows nothing — not even TSP.** Start at file 01 and read
in order. Each file assumes you read the previous ones. Simple words only.

## Reading order

| # | File | What you will learn | Time |
|---|---|---|---|
| 01 | `01_what_is_tsp.md` | What is the delivery-route problem, with zero background | 5 min |
| 02 | `02_the_solvers.md` | Our 5 solution methods, each with a daily-life analogy | 10 min |
| 03 | `03_project_tour.md` | Every folder and file in the project, what it does | 10 min |
| 04 | `04_experiment_small_maps.md` | Experiment 1 (4–9 cities): every chart explained | 15 min |
| 05 | `05_experiment_big_maps.md` | Experiment 2 (10–50 cities): every chart explained | 15 min |
| 06 | `06_results.md` | All result tables + what the numbers mean | 10 min |
| 07 | `07_honest_limits.md` | What we did NOT discover, limits, path to paper level | 5 min |
| 08 | `08_how_to_run.md` | Every command to run everything yourself | 5 min |
| 09 | `09_glossary.md` | Dictionary of all technical words used | 5 min |

## The 2-minute story

A delivery shop has houses to serve. It must start at the shop, visit every
house once, and return. Which order is shortest? That is the **TSP**.

We built **5 different methods** to answer it, from "check everything" to
"quantum dreaming", then raced them fairly on **195 test maps total**
(120 small + 75 big) and plotted every result.

**Headline findings:**
- Small maps (≤9 houses): Genetic Algorithm is near-perfect; QAOA finds the
  exact optimum too (but only fits ≤5 houses in simulation).
- Big maps (10–50 houses): pure Genetic Algorithm collapses (106% worse than
  best at N=50); simple **multi-start 2-opt wins every single map**.
- No quantum computer was used or needed for the classical results.
- Nothing here is new to science (2-opt is from 1958) — but every number is
  ours, measured, and reproducible. Details in file 07.
