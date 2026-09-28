# 04 — Experiment 1: Small Maps (4–9 Cities)

**Notebook:** `notebooks/01_tsp_research_analysis.ipynb`
(already-run pictures: `..._executed.ipynb`)
**Data:** `results/benchmark_results.csv` — 120 rows
(Brute-Force + 3 GA settings × 6 sizes × 10 maps).
**Reference answer:** brute-force optimum (gap = % above optimum).

## Chart 1 — City map + distance heatmap
- **Left (scatter):** the 5 houses as red dots, green star = shop (City 1).
  Read it like a real map: close dots = cheap to travel between.
- **Right (heatmap):** table of every house-to-house distance; darker =
  farther. This table is the raw input every solver sees.
- **Says:** our test map is concrete and checkable — e.g. City 4 sits very
  close to the shop, so good routes visit it first/last.

## Chart 2 — All 24 route lengths (histogram + sorted curve)
- **Histogram:** how the 24 possible lengths spread out. Green dashed line =
  optimum (227.35), red = average route (~a bad guess scores here).
- **Sorted curve:** routes ranked best→worst. Steep at both ends, flat middle.
- **Says:** most random guesses are mediocre; only a few orders are great.
  This is WHY smart methods matter — blind guessing lands in the fat middle.

## Chart 3 — Best vs worst route maps
- Same 5 houses; left map is smooth loop (227.35), right map is a scribble
  crossing itself (332.6). **Crossings = waste.** This visual motivates 2-opt
  (file 02, Racer 3): uncross roads → shorter tour, guaranteed.

## Chart 4 — GA convergence (5 runs overlaid + optimum line)
- X = generation (time), Y = best distance so far. 5 wobbly lines = 5
  independent runs; black dashed = optimum.
- **Says:** all 5 runs dive fast (first ~20 generations do almost all the
  work) then flatten near the optimum. GA learns quickly, then fine-tunes
  slowly. Flat lines at the end = converged.

## Chart 5 — Hyperparameter sensitivity (boxplots, N=7)
- **Left (population 20/50/100):** bigger population → lower and tighter gaps.
  More horses = better breeding.
- **Right (mutation 0.01/0.05/0.15):** 0.05 wins; too little = stuck, too
  much = chaos. Middle creativity is best.
- **Says:** settings matter, and pop-50/mut-0.05 (our default) is justified
  by data, not guesswork.

## Chart 6 — Scaling: runtime (log) + GA gap bars (from the CSV)
- **Runtime (log scale):** brute-force line shoots up steeply (factorial);
  GA lines stay nearly flat. A straight-up line on a log chart = exponential
  explosion — the project's central villain, visualized.
- **Gap bars:** GA mean gap 0% (N=4–6), 0.2% (N=7), ~2% (N=8), ~5% (N=9).
- **Says:** GA trades a few % of perfection for enormous speed. Exactness is
  cheap at N=5, unaffordable at N=12+.

## Chart 7 — 30-trial statistics (N=7)
- **Boxplot:** brute-force (one thin line — always identical, it IS the
  answer) vs GA (short box hugging it — reliably close).
- **Gap histogram:** most trials pile at ~0%; green dashed 1% tolerance line
  shows nearly all runs pass. This is the "is GA lucky or reliable?" answer:
  **reliable** (at this size).
- **Says:** with numbers: mean gap ≈ tiny, success-within-1% ≈ nearly all.

## Chart 8 — Route gallery (4 different maps, optimal routes)
- **Says:** the solver is general — new random map in, correct loop out,
  every time. Not memorized for one map.

## Chart 9 — QAOA roadmap (factorial curve + qubit bars)
- **Left:** (N−1)! search space on log scale with labels (24 → 362,880…) —
  why classical exact methods die.
- **Right:** QAOA qubits needed (N² bars: 25, 36, 49…) — why simulated QAOA
  dies too, but for a different reason (memory, not time).
- **Says:** both exact roads end; heuristics (and one day real quantum
  hardware) are the only way forward.
