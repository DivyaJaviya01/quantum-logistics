# 07 — Honest Limits (Read Before Bragging)

## What we did NOT discover

**Nothing new to science.** Every method here is decades old: 2-opt (1958),
GA-for-TSP (1970s–80s), memetic algorithms (1989), QAOA (2014). Our headline
("simple restarted 2-opt beats pure GA") is textbook knowledge. Concorde solved
85,900-city TSPs years ago — 50 cities impresses no researcher. Claiming
novelty would get a report rejected in one line.

## What IS genuinely ours

1. **Independent replication** — built from scratch, bugs caught by
   measurement (the 2-opt early-stop bug: 1121→978 before fix, 1121→370
   after). Replication with teeth.
2. **Original data** — 195 measured runs nobody else has (120 + 75 CSV rows).
3. **A working lab** — any new idea testable in an afternoon.
4. **Honest negatives** — the QAOA local-minimum trap and pure-GA collapse
   are reported, not hidden. Reviewers trust this.

## Limits of our claims

- Big-map gaps are vs **best-found, not optimum** (unknown at N=50).
- Only **5 trials** per size — ranking is stable but error bars are rough;
  30 trials + significance tests needed for paper level.
- Only **uniform random maps** — 2-opt's dominance may shrink on clustered
  or real road networks (untested).
- QAOA capped at **N ≤ 5** (simulation memory); larger needs real hardware.
- GA budget fixed (pop-60/gen-120); bigger budgets would flatter pure GA.

## Paper-level scorecard: ~2.5 / 5

| Requirement | Status |
|---|---|
| Novel idea/finding | ❌ missing |
| Literature review + citations | ❌ missing |
| Strong statistics (30 trials, tests) | ⚠️ half |
| Honest limits | ✅ have it |
| Reproducible code | ✅ better than most papers |

Student workshops/symposiums: submittable today as a comparative study.
Journal/conference: needs one novel element first.

## Candidate next steps (toward new)

1. **Clustered maps** (cheapest, 1–2 evenings) — may flip the ranking; result
   currently unknown = potentially new.
2. **Fair QAOA-vs-classical shootout** (1 week) — equal time budgets, small N.
3. **Your own hybrid** (2–3 weeks) — e.g. 2-opt-guided crossover, prove the win.
