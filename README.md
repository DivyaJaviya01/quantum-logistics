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
└── utils/                     # Utilities
    └── plotting.py            # Matplotlib plotting functions
```

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

