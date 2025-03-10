import matplotlib
matplotlib.use("TkAgg")  # Use TkAgg for GUI compatibility
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import tkinter as tk
from tkinter import ttk
import numpy as np

# Rule mapping
rule_map = {
    "Rule 30: Chaotic": 30,
    "Rule 90: Sierpiński triangle": 90,
    "Rule 110: Turing-complete": 110,
    "Rule 184: Traffic flow": 184,
    "Rule 22: Nested patterns": 22,
    "Rule 54: Complex structures": 54,
    "Rule 250: All-on replication": 250
}

# Automaton settings
width = 60   # Increased width for better visualization
steps = 40   # Number of time steps

# Initial state: Single active cell in the center
initial_state = np.zeros(width, dtype=int)
initial_state[width // 2] = 1  # Activate center cell

running = False  # Global flag to control animation


def select_rule():
    """Create the GUI for rule selection."""
    global running

    def toggle_animation():
        global running
        running = not running
        if running:
            start_stop_button.config(text="Stop")
            run_simulation()
        else:
            start_stop_button.config(text="Start")

    def get_rule_number():
        return rule_map[rule_var.get()]

    def run_simulation():
        if running:
            simulate(get_rule_number())

    window = tk.Tk()
    window.title("Elementary Cellular Automaton")
    window.geometry("500x300")

    main_frame = ttk.Frame(window, padding=10)
    main_frame.pack(fill='both', expand=True)

    ttk.Label(main_frame, text="Select Rule").grid(row=0, column=0, padx=10, pady=5)
    rule_var = tk.StringVar(value=list(rule_map.keys())[0])
    rule_dropdown = ttk.Combobox(main_frame, textvariable=rule_var, values=list(rule_map.keys()), state="readonly")
    rule_dropdown.grid(row=0, column=1, padx=10, pady=5)

    start_stop_button = ttk.Button(main_frame, text="Start / Stop", command=toggle_animation)
    start_stop_button.grid(row=1, column=0, columnspan=2, pady=10)

    window.mainloop()


def apply_rule(current_state, rule_number):
    """Apply the selected rule to generate the next state."""
    rule_binary = f"{rule_number:08b}"  # Convert rule number to binary
    next_state = np.zeros_like(current_state)

    for i in range(len(current_state)):
        left = current_state[i - 1] if i > 0 else 0
        center = current_state[i]
        right = current_state[i + 1] if i < len(current_state) - 1 else 0

        # Convert neighborhood to decimal
        neighborhood = (left << 2) | (center << 1) | right # representation for 3bit neighbourhood
        next_state[i] = int(rule_binary[7 - neighborhood])  # Apply rule

    return next_state # new state is assigned to i 


def simulate(rule_number):
    """Run and animate the cellular automaton with a grid."""
    global running

    # Initialize grid to store evolution steps
    grid = np.zeros((steps, width), dtype=int)
    grid[0] = initial_state  # Set initial state as first row

    fig, ax = plt.subplots(figsize=(10, 6))  # Larger figure for better visualization

    # Display the grid with minor ticks
    ax.set_xticks(np.arange(-0.5, width, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, steps, 1), minor=True)
    ax.grid(which="minor", color="gray", linestyle="-", linewidth=0.5)

    # Remove major axis labels
    ax.set_xticks([])
    ax.set_yticks([])

    img = ax.imshow(grid, cmap="Greens", aspect="auto", interpolation="none")
    ax.set_title(f"Elementary Cellular Automaton - Rule {rule_number}")

    def evolve(i):
        if running and i < steps - 1:
            grid[i + 1] = apply_rule(grid[i], rule_number)  # Generate next state
            img.set_array(grid)  # Update display
        return [img]

    ani = animation.FuncAnimation(fig, evolve, frames=steps, interval=150, blit=False)
    plt.show()


if __name__ == "__main__":
    select_rule()
