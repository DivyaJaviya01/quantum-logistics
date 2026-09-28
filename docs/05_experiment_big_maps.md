# 05 — Experiment 2: Big Maps (10–50 Cities)

**Notebook:** `notebooks/02_scale_up_memetic.ipynb`
(already-run pictures: `..._executed.ipynb`)
**Data:** `results/benchmark_scale.csv` — 75 rows
(pure GA vs Memetic vs 2-opt×20 × 5 sizes × 5 maps, GA budget pop-60/gen-120).
**Reference answer:** NO optimum exists here (brute-force impossible), so
gap = % above the **best found by any method on that map** (`gap_vs_best`).
Read "0%" as "won this map", not "perfect".

## Chart 1 — Mean gap vs N (with error bars)
- Three lines: pure GA climbs steeply (27% → 44% → 74% → 106%);
  memetic stays low (2% → 6% → 8% → 4%); 2-opt×20 sits at 0% throughout.
- Error bars (±1 std over 5 maps) are small relative to the gaps between
  lines — the ranking is stable, not luck.
- **Says:** pure evolution collapses with size (at N=50 its tours are more
  than TWICE as long as best-found); adding the polisher fixes ~90% of the
  damage; plain restarted polishing wins outright.

## Chart 2 — Mean runtime vs N (+ table)
- X = cities, Y = seconds. All three rise gently (seconds, not hours).
  Measured means: at N=50, pure GA ≈ 5.9 s, memetic ≈ 3.7 s,
  2-opt×20 ≈ 3.8 s per map on this laptop.
- **Says:** everything here is laptop-practical. Compare with brute-force,
  which cannot even START at N=15. Speed was never the problem — quality was,
  and 2-opt solved it.

## Chart 3 — Before/after polish (live N=30 demo, two maps side by side)
- **Left (BEFORE):** raw GA route — visibly tangled, many X-crossings,
  length ~611.
- **Right (AFTER):** same route after 2-opt — smooth loop, ~0 crossings,
  length ~480 (example numbers vary by seed; crossing counter printed above
  the chart quantifies it, e.g. "14 crossings → 0").
- **Says:** the single clearest visual in the project — crossings ARE the
  waste, and removing them is worth ~10–20% for free.

## Chart 4 — Win table (bar chart: who won each of the 5 maps per size)
- Bars show 2-opt×20 winning **all 25 maps** (5/5 at every size).
- **Says:** the surprise headline, stated plainly: the simplest method
  (random starts + polish, no evolution at all) beat the fancy hybrids
  everywhere tested. Simple + stubborn > clever + tangled — on uniform
  random maps (honest scope note: clustered/real-road maps may differ;
  listed as next experiment in file 07).
