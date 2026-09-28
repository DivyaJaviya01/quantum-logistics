# 06 — Results (All Numbers in One Place)

## A. Small maps — gap vs TRUE optimum (%, 10 maps each)

| N | GA default | GA large-pop | GA high-mut |
|---|---|---|---|
| 4 | 0.00 | (same run family) | (same run family) |
| 5 | 0.00 | — | — |
| 6 | 0.00 | — | — |
| 7 | 0.20 | — | — |
| 8 | 1.89 | — | — |
| 9 | 5.45 | — | — |

Source: `results/benchmark_results.csv` (120 rows). Full per-config means are
recomputable with `python -m experiments.benchmark --trials 10
--max-cities 9 --quick`.
**Meaning:** GA is exactly optimal through N=6, then drifts gently
(0.2% → 2% → 5%). Larger populations help more than higher mutation (file 04,
chart 5).

## B. QAOA spot-checks (gap vs TRUE optimum)

| Map | Qubits | Depth | Iterations | Gap |
|---|---|---|---|---|
| N=4 (3 seeds) | 9 | 2 | 60 | 0% all |
| N=5 seed 42 | 16 | 2 | 80 | 0% (exact optimum 227.35) |
| N=5 (3 seeds) | 16 | 2 | 60 | 0%, ~1%, **~17%** |

Source: `test_qaoa.py`, `results/benchmark_qaoa_check.csv`.
**Meaning:** QAOA CAN reach the exact optimum — but with a small optimizer
budget it got trapped in a local minimum on one map (17%). Optimizer budget
matters; that trap is genuine quantum-optimization behaviour and the most
report-worthy QAOA observation in the project.

## C. Big maps — gap vs BEST-FOUND (%, 5 maps each) + mean seconds

| N | pure GA (gap / s) | memetic (gap / s) | 2-opt×20 (gap / s) |
|---|---|---|---|
| 10 | 1.6 / 0.9 | 0.2 / 1.1 | 0.0 / 0.04 |
| 20 | 26.7 / 1.9 | 1.6 / 2.2 | 0.0 / 0.2 |
| 30 | 43.5 / 2.0 | 6.1 / 2.7 | 0.0 / 0.5 |
| 40 | 73.9 / 5.8 | 7.8 / 6.8 | 0.0 / 2.0 |
| 50 | 105.6 / 5.9 | 4.3 / 3.7 | 0.0 / 3.8 |

Source: `results/benchmark_scale.csv` (75 rows). GA budget pop-60/gen-120.
**Meaning:** pure GA more than doubles best-found length by N=50; memetic
stays single-digit %; 2-opt×20 won all 25 maps AND is fastest at small N.
(Remember: 0% = "won", not "perfect" — the true optimum at N=50 is unknown.)

## D. Headline sentences (safe to quote)

1. "On maps up to 9 cities, our GA stays within ~5% of the proven optimum."
2. "At 50 cities, pure GA tours average 106% longer than best-found, while
   memetic stays at ~4% — the 2-opt polish removes ~90% of the damage."
3. "Multi-start 2-opt won all 25 large test maps, running in seconds."
4. "Our QAOA simulation reached the exact optimum at N=4–5, but showed
   local-minimum trapping (~17% gap) under small optimizer budgets."
