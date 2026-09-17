"""TSP Prototype - Quantum-Inspired Optimization for Logistics Routing.

Entry point for the application. Launches Streamlit web server by default.
"""

import sys
import os
import subprocess

# Add project root to path so imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    """Start the TSP application (Streamlit web server by default)."""
    if len(sys.argv) > 1 and sys.argv[1] in ["--gui", "--tkinter"]:
        import tkinter as tk
        from ui.app import TSPApp
        root = tk.Tk()
        app = TSPApp(root)
        root.mainloop()
    else:
        app_path = os.path.join(os.path.dirname(__file__), "ui", "streamlit_app.py")
        print("🚀 Starting Quantum Logistics Streamlit Web Server...")
        subprocess.run([sys.executable, "-m", "streamlit", "run", app_path, "--server.port=8501"])


if __name__ == "__main__":
    main()

