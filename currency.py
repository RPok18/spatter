import tkinter as tk
from tkinter import ttk
import random
import time
import threading
from queue import Queue
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class CurrencySimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("INR/RUB Exchange Rate Simulator")
        self.running = False
        self.queue = Queue()
        self.current_rate1 = 0.0  # INR
        self.current_rate2 = 0.0  # RUB
        self.rate_history1 = []
        self.rate_history2 = []
        self.time_history = []
        self.start_time = None
        self.data_points_count = 12  # Number of data points to show

        # --- Input Frame ---
        self.input_frame = ttk.Frame(root)
        self.input_frame.pack(pady=10)

        # Initial Price 1 (INR)
        self.initial_price1_label = ttk.Label(self.input_frame, text="Initial price INR:")
        self.initial_price1_label.grid(row=0, column=0, padx=5)
        self.initial_price1_var = tk.StringVar()
        self.initial_price1_entry = ttk.Entry(self.input_frame, textvariable=self.initial_price1_var, width=8)
        self.initial_price1_entry.grid(row=0, column=1, padx=5)
        self.initial_price1_var.set("73.0738")  # Set default value

        # Initial Price 2 (RUB)
        self.initial_price2_label = ttk.Label(self.input_frame, text="Initial price RUB:")
        self.initial_price2_label.grid(row=0, column=2, padx=5)
        self.initial_price2_var = tk.StringVar()
        self.initial_price2_entry = ttk.Entry(self.input_frame, textvariable=self.initial_price2_var, width=8)
        self.initial_price2_entry.grid(row=0, column=3, padx=5)
        self.initial_price2_var.set("71.1012")  # Set default value

        # --- Control Buttons ---
        self.button_frame = ttk.Frame(root)
        self.button_frame.pack(pady=10)

        self.start_stop_button = ttk.Button(self.button_frame, text="Start/Stop", command=self.toggle_simulation)
        self.start_stop_button.pack(side=tk.LEFT, padx=5)

        # --- Graph Area ---
        self.graph_frame = ttk.LabelFrame(root, text="Exchange Rate Trend")
        self.graph_frame.pack(pady=10, fill=tk.BOTH, expand=True, padx=10)

        self.fig, self.ax = plt.subplots(figsize=(8, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Grid for the graph
        self.ax.grid(True)

        # --- Labels for the curves
        self.inr_label = "INR"
        self.rub_label = "RUB"

        # --- Error Label ---
        self.error_label = ttk.Label(root, text="", foreground="red")
        self.error_label.pack()

        self.update_gui()

    def validate_inputs(self):
        try:
            # Correctly handle commas by replacing them with periods
            initial_price1_str = self.initial_price1_var.get().replace(",", ".")
            initial_price2_str = self.initial_price2_var.get().replace(",", ".")

            initial_price1 = float(initial_price1_str)
            initial_price2 = float(initial_price2_str)

            if initial_price1 <= 0 or initial_price2 <= 0:
                raise ValueError("Initial prices must be positive")

            return True
        except ValueError as e:
            self.error_label.config(text=str(e) if str(e) else "Invalid input value")
            return False

    def toggle_simulation(self):
        if self.running:
            self.stop_simulation()
        else:
            self.start_simulation()

    def start_simulation(self):
        if self.validate_inputs():
            # Correctly handle commas by replacing them with periods
            initial_price1_str = self.initial_price1_var.get().replace(",", ".")
            initial_price2_str = self.initial_price2_var.get().replace(",", ".")

            self.running = True
            self.current_rate1 = float(initial_price1_str)
            self.current_rate2 = float(initial_price2_str)
            self.rate_history1 = [self.current_rate1]
            self.rate_history2 = [self.current_rate2]
            self.start_time = time.time()
            self.time_history = [0]

            self.start_stop_button.config(text="Stop")  # Change button text
            self.error_label.config(text="")  # Clear any previous errors

            self.simulate_exchange_rate()  # Start the simulation
        else:
            print("Validation failed. Not starting the simulation.")

    def stop_simulation(self):
        self.running = False
        self.start_stop_button.config(text="Start")  # Change button text back
        print("Simulation stopped.")

    def simulate_exchange_rate(self):
        def simulate():
            if not self.running:
                print("Simulation thread exiting...")
                return

            try:
                # Simulate rate changes with small random fluctuations
                self.current_rate1 *= random.uniform(0.995, 1.005)
                self.current_rate2 *= random.uniform(0.995, 1.005)

                current_time = time.time() - self.start_time
                self.rate_history1.append(self.current_rate1)
                self.rate_history2.append(self.current_rate2)
                self.time_history.append(current_time)

                self.update_graph()

            except Exception as e:
                print(f"Error in simulation thread: {e}")
                self.error_label.config(text=f"Simulation error: {str(e)}")
                self.stop_simulation() # Stop on error

            self.root.after(1000, simulate)  # Schedule next update in 1 second
        simulate()  # Start the simulation loop

    def update_graph(self):
        if not self.running:
            return

        # Limit number of points displayed
        num_points = min(len(self.time_history), self.data_points_count)  # Limit to data_points_count
        time_data = self.time_history[-num_points:]
        rate_data1 = self.rate_history1[-num_points:]
        rate_data2 = self.rate_history2[-num_points:]

        # Clear the axes and plot the new data
        self.ax.clear()
        self.ax.grid(True)

        # Plot data
        self.ax.plot(time_data, rate_data1, 'g-', label=self.inr_label)
        self.ax.plot(time_data, rate_data2, 'r-', label=self.rub_label)

        # Set the range for labels to not overlap with the lines
        max_y = max(max(rate_data1), max(rate_data2))
        min_y = min(min(rate_data1), min(rate_data2))
        y_range = max_y - min_y
        self.ax.set_ylim([min_y - 0.05 * y_range, max_y + 0.05 * y_range])

        # Add data point values to graph
        for i in range(len(time_data)):
            # Adding rate1 data
            self.ax.text(time_data[i], rate_data1[i], f'{rate_data1[i]:.4f}', color='green', fontsize=8, ha='center', va='bottom')
            # Adding rate2 data
            self.ax.text(time_data[i], rate_data2[i], f'{rate_data2[i]:.4f}', color='red', fontsize=8, ha='center', va='bottom')

        # Set the limit of x axis to 10 points, so not to overlap the graph
        max_x = max(time_data)
        self.ax.set_xlim([0, max_x if max_x <10 else 10])

        # Add the label and title
        self.ax.set_xlabel('Time (seconds)')
        self.ax.set_ylabel('Exchange Rate')
        self.ax.set_title('INR/RUB Exchange Rate Over Time')

        self.ax.legend()
        self.canvas.draw()  # Redraw

    def update_gui(self):
        self.root.after(100, self.update_gui)

if __name__ == "__main__":
    root = tk.Tk()
    app = CurrencySimulator(root)
    root.mainloop()
