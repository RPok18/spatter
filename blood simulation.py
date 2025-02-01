import tkinter as tk
from tkinter import simpledialog, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Function to simulate blood spatter
def simulate_blood_spatter(velocity, angle_degrees, num_droplets=100):
    angle_radians = np.radians(angle_degrees)
    gravity = 9.81
    time_of_flight = (2 * velocity * np.sin(angle_radians)) / gravity
    x = velocity * np.cos(angle_radians) * time_of_flight
    y = velocity * np.sin(angle_radians) * time_of_flight - 0.5 * gravity * time_of_flight**2

    x_values = x + np.random.normal(0, 0.1, num_droplets)
    y_values = y + np.random.normal(0, 0.1, num_droplets)
    return x_values, y_values

# Function to open a dialog box and get user input
def get_user_input():
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    # Create a custom dialog box
    class InputDialog(tk.Toplevel):
        def __init__(self):
            super().__init__()
            self.title("Blood Spatter Parameters")
            
            # Labels and input fields
            tk.Label(self, text="Velocity (m/s):").grid(row=0, column=0, padx=10, pady=5)
            self.velocity_entry = tk.Entry(self)
            self.velocity_entry.grid(row=0, column=1, padx=10, pady=5)

            tk.Label(self, text="Angle (degrees):").grid(row=1, column=0, padx=10, pady=5)
            self.angle_entry = tk.Entry(self)
            self.angle_entry.grid(row=1, column=1, padx=10, pady=5)

            tk.Label(self, text="Number of Droplets:").grid(row=2, column=0, padx=10, pady=5)
            self.droplets_entry = tk.Entry(self)
            self.droplets_entry.grid(row=2, column=1, padx=10, pady=5)

            tk.Button(self, text="Submit", command=self.on_submit).grid(row=3, column=0, columnspan=2, pady=10)

        def on_submit(self):
            try:
                self.velocity = float(self.velocity_entry.get())
                self.angle = float(self.angle_entry.get())
                self.droplets = int(self.droplets_entry.get())
                self.destroy()
            except ValueError:
                messagebox.showerror("Error", "Invalid input! Please enter numbers.")

    # Open the custom dialog and wait for input
    dialog = InputDialog()
    dialog.wait_window()

    # Return the values if valid
    if hasattr(dialog, 'velocity'):
        return dialog.velocity, dialog.angle, dialog.droplets
    else:
        return None

# Main function to run the program
def main():
    # Get user input from the dialog box
    params = get_user_input()
    if not params:
        return  # Exit if input is invalid

    velocity, angle, droplets = params

    # Simulate blood spatter
    x, y = simulate_blood_spatter(velocity, angle, droplets)

    # Plot the results in a tkinter window
    root = tk.Tk()
    root.title("Blood Spatter Report")

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.scatter(x, y, color='red', s=10)
    ax.set_title("Blood Spatter Pattern")
    ax.set_xlabel("Distance (m)")
    ax.set_ylabel("Height (m)")
    ax.grid(True)

    # Embed the plot in the tkinter window
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack()

    tk.mainloop()

if __name__ == "__main__":
    main()