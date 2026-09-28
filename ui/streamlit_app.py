"""Streamlit Web Application for Quantum-Inspired Logistics TSP Solver."""

import sys
import os
import time

# Ensure project root is in python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import math

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

from core.city_generator import generate_cities
from core.distance import calculate_distance
from algorithms.tsp_bruteforce import solve_tsp_bruteforce
from algorithms.genetic_algorithm import solve_tsp_genetic
from algorithms.memetic import solve_tsp_memetic
from algorithms.qaoa import solve_tsp_qaoa, MAX_CITIES_EXACT


# Page Configuration
st.set_page_config(
    page_title="Quantum Logistics - TSP Optimizer",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling (CSS)
st.markdown(
    """
    <style>
    /* Dark glassmorphism and modern gradient styling */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
        color: #f8fafc;
    }
    .main-header {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(12px);
        padding: 1.5rem 2rem;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    .metric-card {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        background: linear-gradient(90deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def create_plotly_route_map(cities, route=None, title="City Coordinates & Logistics Route"):
    """Create an interactive Plotly map for cities and route visualization."""
    fig = go.Figure()

    n = len(cities)
    df_cities = pd.DataFrame(cities, columns=['X', 'Y'])
    df_cities['City_ID'] = [f"City {i+1}" for i in range(n)]

    # Draw Route Lines if provided
    if route is not None:
        route_indices = route + [route[0]]
        route_x = cities[route_indices, 0]
        route_y = cities[route_indices, 1]

        # Route path line
        fig.add_trace(
            go.Scatter(
                x=route_x,
                y=route_y,
                mode='lines+markers',
                line=dict(color='#38bdf8', width=3, dash='solid'),
                marker=dict(size=8, color='#38bdf8'),
                name='Optimal Route',
                hoverinfo='skip',
            )
        )

        # Draw direction arrows/annotations on legs
        for idx in range(len(route)):
            c1_idx = route[idx]
            c2_idx = route[(idx + 1) % len(route)]
            x1, y1 = cities[c1_idx]
            x2, y2 = cities[c2_idx]
            mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
            leg_dist = np.linalg.norm(cities[c1_idx] - cities[c2_idx])

            fig.add_annotation(
                x=mid_x,
                y=mid_y,
                text=f"{leg_dist:.1f}",
                showarrow=False,
                font=dict(size=10, color="#94a3b8"),
                bgcolor="rgba(15, 23, 42, 0.8)",
                bordercolor="rgba(255, 255, 255, 0.1)",
                borderwidth=1,
                borderpad=2,
            )

    # Draw Non-depot cities
    fig.add_trace(
        go.Scatter(
            x=df_cities.iloc[1:]['X'],
            y=df_cities.iloc[1:]['Y'],
            mode='markers+text',
            marker=dict(size=14, color='#f43f5e', line=dict(width=2, color='#ffffff')),
            text=df_cities.iloc[1:]['City_ID'],
            textposition="top center",
            name='Cities / Hubs',
            hovertemplate="<b>%{text}</b><br>X: %{x:.2f}<br>Y: %{y:.2f}<extra></extra>",
        )
    )

    # Highlight Depot / Start City (City 1)
    fig.add_trace(
        go.Scatter(
            x=[cities[0, 0]],
            y=[cities[0, 1]],
            mode='markers+text',
            marker=dict(size=20, color='#10b981', symbol='star', line=dict(width=2, color='#ffffff')),
            text=['Depot (City 1)'],
            textposition="bottom center",
            name='Depot (Start)',
            hovertemplate="<b>Depot (City 1)</b><br>X: %{x:.2f}<br>Y: %{y:.2f}<extra></extra>",
        )
    )

    fig.update_layout(
        title=dict(text=title, font=dict(size=18, color='#f8fafc')),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(15, 23, 42, 0.6)',
        xaxis=dict(
            title="X Coordinate",
            gridcolor='rgba(255,255,255,0.1)',
            zerolinecolor='rgba(255,255,255,0.2)',
            color='#94a3b8',
        ),
        yaxis=dict(
            title="Y Coordinate",
            gridcolor='rgba(255,255,255,0.1)',
            zerolinecolor='rgba(255,255,255,0.2)',
            color='#94a3b8',
        ),
        legend=dict(
            font=dict(color='#f8fafc'),
            bgcolor='rgba(30, 41, 59, 0.8)',
            bordercolor='rgba(255,255,255,0.1)',
            borderwidth=1,
        ),
        height=550,
        margin=dict(l=40, r=40, t=60, b=40),
    )

    return fig


def main():
    # Header Banner
    st.markdown(
        """
        <div class="main-header">
            <h1 style="margin: 0; font-size: 2.2rem; background: linear-gradient(90deg, #6366f1, #a855f7, #ec4899); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                ⚛️ Quantum Logistics Routing Optimizer
            </h1>
            <p style="margin: 0.5rem 0 0 0; color: #94a3b8; font-size: 1rem;">
                Travelling Salesperson Problem (TSP) optimization powered by Classical Brute-Force, Genetic Evolutionary Algorithms, and Quantum Heuristics.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Sidebar Controls
    st.sidebar.header("⚙️ Problem Settings")

    num_cities = st.sidebar.slider("Number of Cities (N)", min_value=4, max_value=25, value=7, step=1)

    # Seed management
    if "seed" not in st.session_state:
        st.session_state.seed = 42

    col_seed1, col_seed2 = st.sidebar.columns([3, 2])
    with col_seed1:
        seed_input = st.number_input("Random Seed", value=st.session_state.seed, step=1)
        st.session_state.seed = seed_input
    with col_seed2:
        st.write("")
        st.write("")
        if st.button("🎲 Random", use_container_width=True):
            st.session_state.seed = int(np.random.randint(1, 99999))
            st.rerun()

    # Generate cities array
    cities = generate_cities(n=num_cities, seed=st.session_state.seed)

    # City Editor Option
    with st.sidebar.expander("📝 View / Edit City Coordinates"):
        df_cities_input = pd.DataFrame(cities, columns=['X', 'Y'])
        df_cities_input.index = [f"City {i+1}" for i in range(num_cities)]
        edited_df = st.data_editor(df_cities_input, num_rows="fixed")
        cities = edited_df[['X', 'Y']].to_numpy()

    st.sidebar.divider()
    st.sidebar.header("🧠 Algorithm Selection")

    algo_choice = st.sidebar.radio(
        "Choose Optimization Solver:",
        [
            "⚡ Brute-Force (Exact)",
            "🧬 Genetic Algorithm (Evolutionary)",
            "🧬➕ Memetic (GA + 2-opt)",
            "⚛️ QAOA (Quantum Simulation)",
            "📊 Benchmark Comparison (All)",
        ],
    )

    # Algorithm specific parameters
    ga_pop_size = 50
    ga_generations = 100
    ga_mutation = 0.05

    if ("Genetic Algorithm" in algo_choice or "Memetic" in algo_choice
            or "Benchmark" in algo_choice):
        with st.sidebar.expander("⚙️ Genetic Algorithm Hyperparameters", expanded=True):
            ga_pop_size = st.slider("Population Size", 10, 200, 50, step=10)
            ga_generations = st.slider("Generations", 20, 500, 100, step=20)
            ga_mutation = st.slider("Mutation Rate", 0.01, 0.30, 0.05, step=0.01)

    # Main content layout
    if algo_choice == "⚡ Brute-Force (Exact)":
        st.subheader("⚡ Brute-Force Solver")
        if num_cities > 11:
            st.warning(
                f"⚠️ Brute-force evaluates {math.factorial(num_cities-1):,} permutations! "
                "For N > 11, execution may take several seconds or minutes."
            )

        col_left, col_right = st.columns([3, 2])

        start_time = time.time()
        best_route, best_distance = solve_tsp_bruteforce(cities)
        exec_time = (time.time() - start_time) * 1000  # ms

        with col_left:
            fig_map = create_plotly_route_map(
                cities, best_route, f"Optimal Route (Brute-Force) — Distance: {best_distance:.2f}"
            )
            st.plotly_chart(fig_map, use_container_width=True)

        with col_right:
            st.markdown("### 📈 Key Results")

            m1, m2 = st.columns(2)
            with m1:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-value">{best_distance:.2f}</div>
                        <div class="metric-label">Min Route Distance</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with m2:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-value">{exec_time:.2f} ms</div>
                        <div class="metric-label">Compute Time</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.write("")
            st.markdown("#### 🔄 Route Order:")
            route_str = " ➔ ".join([f"**City {c+1}**" for c in best_route]) + f" ➔ **City {best_route[0]+1}**"
            st.info(route_str)

            # Leg-by-leg details table
            st.markdown("#### 📋 Route Breakdown")
            leg_data = []
            for i in range(len(best_route)):
                from_c = best_route[i]
                to_c = best_route[(i + 1) % len(best_route)]
                dist = np.linalg.norm(cities[from_c] - cities[to_c])
                leg_data.append(
                    {
                        "Step": i + 1,
                        "From Hub": f"City {from_c+1}",
                        "To Hub": f"City {to_c+1}",
                        "Distance": round(dist, 2),
                    }
                )
            st.dataframe(pd.DataFrame(leg_data), hide_index=True, use_container_width=True)

    elif algo_choice in ("🧬 Genetic Algorithm (Evolutionary)",
                           "🧬➕ Memetic (GA + 2-opt)"):
        is_memetic = algo_choice.startswith("🧬➕")
        st.subheader("🧬➕ Memetic Solver (GA + 2-opt polish)" if is_memetic
                     else "🧬 Genetic Algorithm Solver")

        col_left, col_right = st.columns([3, 2])

        start_time = time.time()
        polish_gain = 0.0
        if is_memetic:
            best_route, best_distance, m_info = solve_tsp_memetic(
                cities,
                population_size=ga_pop_size,
                generations=ga_generations,
                mutation_rate=ga_mutation,
            )
            history = m_info["history"]
            polish_gain = m_info["polish_gain"]
        else:
            best_route, best_distance, history = solve_tsp_genetic(
                cities,
                population_size=ga_pop_size,
                generations=ga_generations,
                mutation_rate=ga_mutation,
            )
        exec_time = (time.time() - start_time) * 1000

        with col_left:
            fig_map = create_plotly_route_map(
                cities, best_route, f"Optimized Route — Distance: {best_distance:.2f}"
            )
            st.plotly_chart(fig_map, use_container_width=True)

        with col_right:
            st.markdown("### 📈 Key Results")

            m1, m2 = st.columns(2)
            with m1:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-value">{best_distance:.2f}</div>
                        <div class="metric-label">Best Distance</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with m2:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-value">{exec_time:.2f} ms</div>
                        <div class="metric-label">Execution Time</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            if is_memetic:
                st.info(f"✨ 2-opt polish shaved off **{polish_gain:.2f}** "
                        f"from the raw GA route.")

            st.write("")
            st.markdown("#### 📉 Fitness Convergence:")

            # Convergence plot with Plotly
            fig_history = go.Figure()
            fig_history.add_trace(
                go.Scatter(
                    y=history,
                    mode='lines',
                    line=dict(color='#818cf8', width=2),
                    fill='tozeroy',
                    fillcolor='rgba(129, 140, 248, 0.1)',
                    name='Best Distance',
                )
            )
            fig_history.update_layout(
                title="Best Distance vs. Generation",
                xaxis_title="Generation",
                yaxis_title="Route Distance",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(15, 23, 42, 0.6)',
                font=dict(color='#94a3b8'),
                height=250,
                margin=dict(l=40, r=40, t=40, b=40),
            )
            st.plotly_chart(fig_history, use_container_width=True)

            st.markdown("#### 🔄 Route Order:")
            route_str = " ➔ ".join([f"**City {c+1}**" for c in best_route]) + f" ➔ **City {best_route[0]+1}**"
            st.info(route_str)

    elif algo_choice == "⚛️ QAOA (Quantum Simulation)":
        st.subheader("⚛️ Quantum Approximate Optimization Algorithm (QAOA)")

        st.info(
            "ℹ️ **Real QAOA simulation** (NumPy statevector + COBYLA optimizer, no Qiskit needed). "
            "TSP is mapped to a QUBO with the depot fixed, needing $(N-1)^2$ qubits. "
            f"Exact simulation supports N ≤ {MAX_CITIES_EXACT}."
        )

        with st.sidebar.expander("⚛️ QAOA Hyperparameters", expanded=True):
            qaoa_depth = st.slider("Circuit Depth (p)", 1, 4, 2, step=1)
            qaoa_maxiter = st.slider("Optimizer Iterations", 20, 200, 80, step=20)

        if num_cities > MAX_CITIES_EXACT:
            st.warning(
                f"⚠️ QAOA exact simulation supports N ≤ {MAX_CITIES_EXACT} "
                f"({(MAX_CITIES_EXACT - 1) ** 2} qubits). "
                f"N={num_cities} would need {(num_cities - 1) ** 2} qubits "
                f"({2 ** ((num_cities - 1) ** 2):,} amplitudes). "
                "Reduce the number of cities to run QAOA."
            )
        else:
            with st.spinner("🔬 Optimizing QAOA variational parameters..."):
                start_time = time.time()
                best_route_q, best_dist_q, q_info = solve_tsp_qaoa(
                    cities, depth=qaoa_depth, maxiter=qaoa_maxiter
                )
                exec_time = (time.time() - start_time) * 1000

            # Exact optimum for reference (cheap at N<=5)
            _, best_dist_bf = solve_tsp_bruteforce(cities)
            gap = (best_dist_q - best_dist_bf) / best_dist_bf * 100

            col_left, col_right = st.columns([3, 2])

            with col_left:
                fig_map = create_plotly_route_map(
                    cities, best_route_q, f"QAOA Ground State Route — Distance: {best_dist_q:.2f}"
                )
                st.plotly_chart(fig_map, use_container_width=True)

            with col_right:
                st.markdown("### ⚛️ Quantum Circuit Parameters")
                st.markdown("- **Qubits Used**: $(N-1)^2 = %d$" % q_info["qubits"])
                st.markdown("- **Circuit Layers ($p$)**: %d" % q_info["depth"])
                st.markdown("- **Mixer Hamiltonian**: $H_M = \\sum X_i$")
                st.markdown("- **Cost Hamiltonian**: $H_C = \\sum d_{ij} x_{i,p} x_{j,p+1} + \\lambda \\text{Penalties}$")
                st.markdown("- **Top-state probability**: %.4f" % q_info["top_prob"])
                st.markdown("- **Optimality gap**: %.2f%%" % gap)

                # Optimizer convergence
                fig_hist = go.Figure()
                fig_hist.add_trace(
                    go.Scatter(
                        y=q_info["history"], mode="lines+markers",
                        line=dict(color="#a855f7", width=2),
                        name="Mean energy <H_C>",
                    )
                )
                fig_hist.update_layout(
                    title="QAOA optimizer convergence",
                    xaxis_title="COBYLA iteration",
                    yaxis_title="Energy",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(15, 23, 42, 0.6)",
                    font=dict(color="#94a3b8"),
                    height=250,
                    margin=dict(l=40, r=40, t=40, b=40),
                )
                st.plotly_chart(fig_hist, use_container_width=True)

                m1, m2 = st.columns(2)
                with m1:
                    st.markdown(
                        f"""
                        <div class="metric-card">
                            <div class="metric-value">{best_dist_q:.2f}</div>
                            <div class="metric-label">QAOA Distance</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with m2:
                    st.markdown(
                        f"""
                        <div class="metric-card">
                            <div class="metric-value">{exec_time:.0f} ms</div>
                            <div class="metric-label">Sim Time</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                st.markdown("#### 🔄 Route Order:")
                route_str = " ➔ ".join([f"**City {c+1}**" for c in best_route_q]) + f" ➔ **City {best_route_q[0]+1}**"
                st.info(route_str)

    elif algo_choice == "📊 Benchmark Comparison (All)":
        st.subheader("📊 Solver Benchmark Comparison")

        col1, col2 = st.columns(2)

        # Run Brute Force
        start_bf = time.time()
        route_bf, dist_bf = solve_tsp_bruteforce(cities)
        time_bf = (time.time() - start_bf) * 1000

        # Run GA
        start_ga = time.time()
        route_ga, dist_ga, _ = solve_tsp_genetic(
            cities, population_size=ga_pop_size, generations=ga_generations, mutation_rate=ga_mutation
        )
        time_ga = (time.time() - start_ga) * 1000

        with col1:
            fig_bf = create_plotly_route_map(
                cities, route_bf, f"Brute-Force (Dist: {dist_bf:.2f}, Time: {time_bf:.1f}ms)"
            )
            st.plotly_chart(fig_bf, use_container_width=True)

        with col2:
            fig_ga = create_plotly_route_map(
                cities, route_ga, f"Genetic Algorithm (Dist: {dist_ga:.2f}, Time: {time_ga:.1f}ms)"
            )
            st.plotly_chart(fig_ga, use_container_width=True)

        # Real QAOA when simulable, else mark as N/A
        rows = [
            {
                "Algorithm": "⚡ Brute-Force",
                "Best Distance": round(dist_bf, 2),
                "Execution Time (ms)": round(time_bf, 2),
                "Optimality Guarantee": "100% (Global Optimum)",
            },
            {
                "Algorithm": "🧬 Genetic Algorithm",
                "Best Distance": round(dist_ga, 2),
                "Execution Time (ms)": round(time_ga, 2),
                "Optimality Guarantee": f"{min(100.0, (dist_bf/dist_ga)*100):.1f}% Approx.",
            },
        ]
        if num_cities <= MAX_CITIES_EXACT:
            with st.spinner("🔬 Running QAOA for benchmark..."):
                start_q = time.time()
                _, dist_q, _ = solve_tsp_qaoa(cities, depth=2, maxiter=60)
                time_q = (time.time() - start_q) * 1000
            rows.append(
                {
                    "Algorithm": "⚛️ QAOA (Quantum Sim)",
                    "Best Distance": round(dist_q, 2),
                    "Execution Time (ms)": round(time_q, 2),
                    "Optimality Guarantee": f"{min(100.0, (dist_bf/dist_q)*100):.1f}% Approx.",
                }
            )
        else:
            rows.append(
                {
                    "Algorithm": "⚛️ QAOA (Quantum Sim)",
                    "Best Distance": "N/A (N>5)",
                    "Execution Time (ms)": "N/A",
                    "Optimality Guarantee": "Needs real quantum hardware",
                }
            )

        # Summary Benchmark Data Table
        st.markdown("### 🏆 Performance Breakdown")
        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

    # Footer
    st.divider()
    st.caption(
        "⚛️ Quantum Logistics Routing Prototype | Built with Streamlit, Plotly, NumPy & Matplotlib"
    )


if __name__ == "__main__":
    main()
