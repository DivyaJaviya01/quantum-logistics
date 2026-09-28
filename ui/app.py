"""Tkinter UI for TSP application."""

import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from core.city_generator import generate_cities
from algorithms.tsp_bruteforce import solve_tsp_bruteforce
from algorithms.genetic_algorithm import solve_tsp_genetic
from utils.plotting import plot_cities, plot_route


class TSPApp:
    """Main Tkinter application for TSP visualization."""

    def __init__(self, root):
        self.root = root
        self.root.title("TSP Prototype - Quantum-Inspired Logistics")

        self.cities = None
        self.best_route = None
        self.best_distance = None
        self.history = None

        # Controls frame
        controls = ttk.Frame(root, padding=10)
        controls.pack(side=tk.TOP, fill=tk.X)

        self.btn_generate = ttk.Button(controls, text="Generate Cities", command=self.generate_cities)
        self.btn_generate.pack(side=tk.LEFT, padx=5)

        # Algorithm selector
        ttk.Label(controls, text="Algorithm:").pack(side=tk.LEFT, padx=(20, 5))
        self.algorithm_var = tk.StringVar(value="Brute-Force")
        self.algorithm_menu = ttk.Combobox(
            controls,
            textvariable=self.algorithm_var,
            values=["Brute-Force", "Genetic Algorithm"],
            state="readonly",
            width=18
        )
        self.algorithm_menu.pack(side=tk.LEFT, padx=5)

        self.btn_solve = ttk.Button(controls, text="Solve TSP", command=self.solve_tsp, state=tk.DISABLED)
        self.btn_solve.pack(side=tk.LEFT, padx=5)

        self.label_distance = ttk.Label(controls, text="Distance: ---")
        self.label_distance.pack(side=tk.LEFT, padx=20)

        # Matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(6, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def generate_cities(self):
        """Generate new random cities and reset solver state."""
        self.cities = generate_cities(n=5)
        self.best_route = None
        self.best_distance = None
        self.history = None
        self.btn_solve.config(state=tk.NORMAL)
        self.label_distance.config(text="Distance: ---")
        plot_cities(self.ax, self.cities)
        self.canvas.draw()

    def solve_tsp(self):
        """Run selected solver and display the result."""
        if self.cities is None:
            return

        algorithm = self.algorithm_var.get()

        if algorithm == "Brute-Force":
            self.best_route, self.best_distance = solve_tsp_bruteforce(self.cities)
            self.history = None
        else:
            self.best_route, self.best_distance, self.history = solve_tsp_genetic(
                self.cities,
                population_size=50,
                generations=100,
                mutation_rate=0.05
            )

        self.label_distance.config(text=f"Distance: {self.best_distance:.2f}")
        plot_route(self.ax, self.cities, self.best_route)
        self.canvas.draw()
