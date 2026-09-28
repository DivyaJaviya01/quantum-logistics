# Quantum-Inspired Optimization for Logistics Routing

Prototype TSP solver for the research project featuring Streamlit interactive Web Dashboard and Tkinter desktop UI.

📄 **Documentation**:
- 📌 [Problem Statement & Research Specifications](PROBLEM_STATEMENT.md)
- 🚀 [Phase-Wise Development Report](PHASE_REPORT.md)

## Structure

```
quantum-logistics/
├── PROBLEM_STATEMENT.md       # Research problem specification & architecture
├── PHASE_REPORT.md            # Phase-by-phase implementation progress & roadmap
├── main.py                    # Entry point (launches Streamlit web server)

├── algorithms/                # TSP solvers
│   ├── tsp_bruteforce.py      # Brute-force solver (exact)
│   ├── genetic_algorithm.py   # Genetic Algorithm evolutionary solver
│   └── qaoa.py                # QAOA quantum solver simulation
├── core/                      # Core logic
│   ├── city_generator.py      # City coordinate generation
│   └── distance.py            # Route distance calculation
├── ui/                        # User interfaces
│   ├── streamlit_app.py       # Streamlit web dashboard
│   └── app.py                 # Tkinter desktop UI
├── utils/                     # Utilities
│   ├── plotting.py            # Matplotlib plotting functions
│   └── metrics.py             # Optimality gap, distance matrix, summaries
├── experiments/               # Benchmarking
│   └── benchmark.py           # Systematic BF vs GA benchmark -> results CSV
├── notebooks/                 # Research analysis
│   ├── 01_tsp_research_analysis.ipynb          # Main analysis (run this)
│   └── 01_tsp_research_analysis_executed.ipynb # Executed version with plots
└── results/                   # Benchmark outputs
    └── benchmark_results.csv  # 120 records (N=4..9, 10 trials)
```

## Research Notebook (ipynb)

Full charts + analysis — open in JupyterLab:

```bash
jupyter lab notebooks/01_tsp_research_analysis.ipynb
```

Covers: instance visualisation, distance-matrix heatmap, all-24-routes
landscape, GA convergence (5 runs), hyperparameter sensitivity,
scaling study (runtime log-plot + optimality gap), 30-trial statistics,
route gallery, and QAOA roadmap (qubit scaling chart).

## Benchmark Suite

```bash
python -m experiments.benchmark --trials 10 --max-cities 9 --quick
```

Key finding: GA is optimal at N<=6, gap ~0.2% at N=7, ~2% at N=8, ~5% at N=9.

## QAOA Solver (real simulation, free tools)

`algorithms/qaoa.py` implements actual QAOA with NumPy statevector +
SciPy COBYLA — no Qiskit, no paid API.

```bash
python test_qaoa.py
python -m experiments.benchmark --trials 3 --max-cities 5 --quick --include-qaoa
```

- TSP mapped to QUBO with depot fixed: only (N-1)^2 qubits (16 for N=5).
- Exact simulation supports N<=5; larger N needs real quantum hardware.
- Measured: optimal (0% gap) at N=4 always; at N=5 optimal with enough
  optimizer iterations, but COBYLA can stick in local minima (~17% gap on
  one seed at maxiter=60) — honest QAOA behaviour, good research material.
- Streamlit QAOA tab runs the real solver with depth/iteration sliders +
  optimizer convergence plot; benchmark tab includes real QAOA numbers.

## Run

### Streamlit Web Server (Default)
```bash
python main.py
# OR
streamlit run ui/streamlit_app.py
```
Access in browser: `http://localhost:8501`

### Desktop Tkinter UI
```bash
python main.py --tkinter
```

