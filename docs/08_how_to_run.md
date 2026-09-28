# 08 — How to Run Everything

All commands run from inside `quantum-logistics/`.

```bash
cd quantum-logistics
```

## Install (once)

```bash
pip install -r requirements.txt
```

Free tools only: numpy, matplotlib, pandas, seaborn, plotly, streamlit,
scipy, scikit-learn, jupyter. No paid API, no Qiskit needed.

## 1. See all charts (nothing to run)

Open in VS Code (pictures already inside):
- `notebooks/01_tsp_research_analysis_executed.ipynb` — small maps
- `notebooks/02_scale_up_memetic_executed.ipynb` — big maps

## 2. Re-run the notebooks yourself

```bash
jupyter lab notebooks/01_tsp_research_analysis.ipynb
jupyter lab notebooks/02_scale_up_memetic.ipynb
```
Click **Run All** in each. Notebook 01: ~1–2 min. Notebook 02: ~2–3 min
(one live GA+polish demo included).

## 3. Open the website

```bash
python main.py
```
Browser: http://localhost:8501
Pick a solver → Generate Cities → Solve TSP.
Try "Memetic (GA + 2-opt)" at 20+ cities; try QAOA at ≤5 cities.

Desktop version: `python main.py --tkinter`

## 4. Health checkups (is each solver healthy?)

```bash
python test_ga.py       # GA vs brute-force, expect OPTIMAL
python test_qaoa.py     # QAOA vs brute-force at N=4,5, expect 0% gaps
python test_memetic.py  # pure GA vs memetic at 10–50 cities
```

## 5. Re-run the science races (regenerate CSVs)

```bash
# Small maps: BF + GA (10 trials, N=4..9)
python -m experiments.benchmark --trials 10 --max-cities 9 --quick

# + QAOA spot-checks (N<=5 only, slower)
python -m experiments.benchmark --trials 3 --max-cities 5 --quick --include-qaoa

# Big maps: pure GA vs memetic vs 2-opt x20 (N=10..50)
python -m experiments.benchmark --scale --trials 5
```

Outputs land in `results/`. Never use `--max-cities` above 10 without
`--scale` (brute-force will hang on factorial explosion — the code refuses).
