import matplotlib
matplotlib.use("TkAgg")  # Use TkAgg for GUI compatibility
import cellpylib as cpl
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

# Initial state (padded to maintain width)
width = 20  # Adjusted width for better visualization
initial_state = np.zeros((6, width), dtype=int)
pattern = [
    [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 0],
    [0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0],
    [0, 0, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1],
    [0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0],
    [0, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0]
]
initial_state[:len(pattern)] = np.array(pattern)

# GUI for rule selection
def select_rule():
    global running
    running = False

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

    ttk.Label(main_frame, text="Rule").grid(row=0, column=0, padx=10, pady=5)
    rule_var = tk.StringVar(value=list(rule_map.keys())[0])
    rule_dropdown = ttk.Combobox(main_frame, textvariable=rule_var, values=list(rule_map.keys()), state="readonly")
    rule_dropdown.grid(row=0, column=1, padx=10, pady=5)

    start_stop_button = ttk.Button(main_frame, text="Start / Stop", command=toggle_animation)
    start_stop_button.grid(row=1, column=0, columnspan=2, pady=10)

    window.mainloop()

# Rule application function
def apply_rule(current_state, rule_number):
    """
    Apply the selected rule to the current state to generate the next state.
    This function will be specific to the rule.
    """
    rule_binary = f"{rule_number:08b}"  # Convert rule number to 8-bit binary string
    next_state = np.zeros_like(current_state)

    # Loop through each cell and apply the rule
    for i in range(1, len(current_state) - 1):
        # Get the neighborhood (previous, current, next)
        neighborhood = (current_state[i - 1] << 2) | (current_state[i] << 1) | current_state[i + 1]
        # Apply the rule based on the neighborhood
        next_state[i] = int(rule_binary[7 - neighborhood], 2)

    return next_state

# Cellular automaton simulation
def simulate(rule_number):
    global running
    running = True
    steps = 20
    grid = np.zeros((steps + len(initial_state), width), dtype=int)
    grid[:len(initial_state)] = initial_state

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.set_xticks(np.arange(-.5, width, 1), minor=True)
    ax.set_yticks(np.arange(-.5, steps + len(initial_state), 1), minor=True)
    ax.grid(which="minor", color='black', linestyle='-', linewidth=1)
    ax.tick_params(which="both", left=False, bottom=False, labelleft=True, labelbottom=False)
    img = ax.imshow(grid, cmap='Greens', aspect='auto', origin='upper', interpolation='none')
    ax.set_title(f"Elementary Cellular Automaton Rule {rule_number}")

    def evolve(i):
        if running and i < steps:
            new_state = apply_rule(grid[i + len(initial_state) - 1], rule_number)
            grid[i + len(initial_state)] = new_state  # Update grid with new state
            img.set_array(grid)
        return [img]

    ani = animation.FuncAnimation(fig, evolve, frames=steps, interval=200, blit=False)
    plt.show()

if __name__ == "__main__":
    select_rule()
