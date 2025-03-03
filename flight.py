import numpy as np
import matplotlib.pyplot as plt
from tkinter import Tk, Label, Button, Entry, StringVar, Toplevel, END, Checkbutton, ttk
from datetime import datetime
import os

# Constants
C = 0.47  # Drag coefficient
rho_0 = 1.225  # Air density at sea level (kg/m^3)
g = 9.81  # Gravity (m/s^2)
H = 8500  # Scale height for Earth's atmosphere (m)

class Projectile:
    def __init__(self, v0, angle, height, size, weight):
        self.v0 = v0
        self.angle = np.deg2rad(angle)
        self.height = height
        self.size = size
        self.weight = weight
        self.cosa = np.cos(self.angle)
        self.sina = np.sin(self.angle)
        self.vx = self.v0 * self.cosa
        self.vy = self.v0 * self.sina
        self.x = 0
        self.y = self.height
        self.t = 0
        self.on_ground = False

    def air_density(self, h):
        """Calculate air density at a given altitude using the barometric formula."""
        return rho_0 * np.exp(-h / H)

    def derivatives(self, t, vx, vy):
        v = np.sqrt(vx**2 + vy**2)
        rho = self.air_density(self.y)  # Dynamic air density based on altitude
        k = 0.5 * C * rho * self.size / self.weight  # Update k with dynamic air density
        dvx_dt = -k * vx * v
        dvy_dt = -g - k * vy * v
        dx_dt = vx
        dy_dt = vy
        return dx_dt, dy_dt, dvx_dt, dvy_dt

    def runge_kutta(self, dt):
        if not self.on_ground:
            dx_dt, dy_dt, dvx_dt, dvy_dt = self.derivatives(self.t, self.vx, self.vy)

            k1_x = dt * dx_dt
            k1_y = dt * dy_dt
            k1_vx = dt * dvx_dt
            k1_vy = dt * dvy_dt

            dx_dt, dy_dt, dvx_dt, dvy_dt = self.derivatives(self.t + dt/2, self.vx + k1_vx/2, self.vy + k1_vy/2)
            k2_x = dt * dx_dt
            k2_y = dt * dy_dt
            k2_vx = dt * dvx_dt
            k2_vy = dt * dvy_dt

            dx_dt, dy_dt, dvx_dt, dvy_dt = self.derivatives(self.t + dt/2, self.vx + k2_vx/2, self.vy + k2_vy/2)
            k3_x = dt * dx_dt
            k3_y = dt * dy_dt
            k3_vx = dt * dvx_dt
            k3_vy = dt * dvy_dt

            dx_dt, dy_dt, dvx_dt, dvy_dt = self.derivatives(self.t + dt, self.vx + k3_vx, self.vy + k3_vy)
            k4_x = dt * dx_dt
            k4_y = dt * dy_dt
            k4_vx = dt * dvx_dt
            k4_vy = dt * dvy_dt

            self.x += (k1_x + 2*k2_x + 2*k3_x + k4_x) / 6
            self.y += (k1_y + 2*k2_y + 2*k3_y + k4_y) / 6
            self.vx += (k1_vx + 2*k2_vx + 2*k3_vx + k4_vx) / 6
            self.vy += (k1_vy + 2*k2_vy + 2*k3_vy + k4_vy) / 6

            self.t += dt

            if self.y < 0:
                self.y = 0
                self.on_ground = True
                self.vx = 0
                self.vy = 0

    def calculate_max_height(self):
        return self.height + (self.v0**2 * self.sina**2) / (2 * g)

    def calculate_distance(self):
        return self.x

    def calculate_speed_at_end(self):
        return self.vx

class SimulationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Projectile Simulation with Atmosphere")
        self.dt = 0.1  # Time step (s)
        self.simulation_count = 0
        self.comparison_projectiles = []
        self.x_values = []
        self.y_values = []

        # Input fields
        self.height_label = Label(root, text="Initial Height (m):")
        self.height_label.pack()
        self.height_entry = Entry(root)
        self.height_entry.pack()

        self.angle_label = Label(root, text="Launch Angle (degrees):")
        self.angle_label.pack()
        self.angle_entry = Entry(root)
        self.angle_entry.pack()

        self.speed_label = Label(root, text="Initial Speed (m/s):")
        self.speed_label.pack()
        self.speed_entry = Entry(root)
        self.speed_entry.pack()

        self.size_label = Label(root, text="Cross-sectional Area (m^2):")
        self.size_label.pack()
        self.size_entry = Entry(root)
        self.size_entry.pack()

        self.weight_label = Label(root, text="Mass (kg):")
        self.weight_label.pack()
        self.weight_entry = Entry(root)
        self.weight_entry.pack()

        # Checkbutton for comparison mode
        self.compare_var = StringVar(value="0")
        self.compare_check = Checkbutton(root, text="Add to Comparison", variable=self.compare_var, onvalue="1", offvalue="0")
        self.compare_check.pack()

        # Label and Entry for Time Step
        self.dt_label = Label(root, text="Time Step (s):")
        self.dt_label.pack()
        self.dt_entry = Entry(root)
        self.dt_entry.insert(0, str(self.dt))
        self.dt_entry.pack()

        # Button to start simulation
        simulate_button = Button(root, text="Simulate", command=self.start_simulation)
        simulate_button.pack()

        # Plotting area
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.ax.set_xlabel('Horizontal Distance (m)')
        self.ax.set_ylabel('Height (m)')
        self.ax.set_title('Projectile Trajectory with Atmosphere')
        self.ax.grid(True)
        plt.ion()
        plt.show(block=False)

    def start_simulation(self):
        try:
            v0 = float(self.speed_entry.get())
            angle = float(self.angle_entry.get())
            height = float(self.height_entry.get())
            size = float(self.size_entry.get())
            weight = float(self.weight_entry.get())
            self.dt = float(self.dt_entry.get())

            if not all(isinstance(val, float) and val >= 0 for val in [v0, angle, height, size, weight, self.dt]):
                raise ValueError("All input values must be non-negative numbers.")
            if angle > 90:
                raise ValueError("Launch angle must be between 0 and 90 degrees.")

            self.projectile = Projectile(v0, angle, height, size, weight)
            self.x_values = [self.projectile.x]
            self.y_values = [self.projectile.y]

            self.animate()

        except ValueError as e:
            print(f"Error: {e}")

    def animate(self):
        if not self.projectile.on_ground:
            self.update_plot()
            self.root.after(int(self.dt * 1000), self.animate)
        else:
            distance = self.projectile.calculate_distance()
            max_height = self.projectile.calculate_max_height()
            speed_at_end = self.projectile.calculate_speed_at_end()
            self.display_results(v0=self.projectile.v0, angle=np.rad2deg(self.projectile.angle), height=self.projectile.height, size=self.projectile.size, weight=self.projectile.weight, distance=distance, max_height=max_height, speed_at_end=speed_at_end, time_step=self.dt)
            self.simulation_count += 1
            if self.compare_var.get() == "1":
                self.comparison_projectiles.append({
                    'x': self.x_values,
                    'y': self.y_values,
                    'label': f"Simulation {self.simulation_count}"
                })
                self.compare_var.set("0")
                self.compare_check.deselect()

    def update_plot(self):
        self.projectile.runge_kutta(self.dt)
        self.x_values.append(self.projectile.x)
        self.y_values.append(self.projectile.y)

        self.ax.clear()

        for proj in self.comparison_projectiles:
            self.ax.plot(proj['x'], proj['y'], label=proj['label'], linestyle='--')

        self.ax.plot(self.x_values, self.y_values, label=f"Simulation {self.simulation_count + 1}", linewidth=2)
        self.ax.set_xlabel('Horizontal Distance (m)')
        self.ax.set_ylabel('Height (m)')
        self.ax.set_title('Projectile Trajectory with Atmosphere')
        self.ax.grid(True)

        self.ax.legend()
        plt.draw()
        plt.pause(0.01)

    def display_results(self, v0, angle, height, size, weight, distance, max_height, speed_at_end, time_step):
        self.results_window = Toplevel(self.root)
        self.results_window.title("Simulation Results")

        self.tree = ttk.Treeview(self.results_window, columns=(
            "Simulation", "Timestamp", "Speed", "Angle", "Height", "Size", "Weight", "Distance", "Max Height", "End Speed", "Time Step"
        ), show="headings")

        self.tree.heading("Simulation", text="Simulation #")
        self.tree.heading("Timestamp", text="Timestamp")
        self.tree.heading("Speed", text="Speed (m/s)")
        self.tree.heading("Angle", text="Angle (deg)")
        self.tree.heading("Height", text="Height (m)")
        self.tree.heading("Size", text="Size (m^2)")
        self.tree.heading("Weight", text="Weight (kg)")
        self.tree.heading("Distance", text="Distance (m)")
        self.tree.heading("Max Height", text="Max Height (m)")
        self.tree.heading("End Speed", text="End Speed (m/s)")
        self.tree.heading("Time Step", text="Time Step (s)")

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.tree.insert("", END, values=(
            self.simulation_count + 1,
            timestamp,
            f"{v0:.2f}",
            f"{angle:.2f}",
            f"{height:.2f}",
            f"{size:.2f}",
            f"{weight:.2f}",
            f"{distance:.2f}",
            f"{max_height:.2f}",
            f"{speed_at_end:.2f}",
            f"{time_step:.3f}"
        ))

        self.tree.pack(padx=10, pady=10)

        self.load_results()
        self.save_results(v0, angle, height, size, weight, distance, max_height, speed_at_end, time_step)

        view_button = Button(self.results_window, text="View Previous Results", command=self.view_previous_results)
        view_button.pack()

        clear_comparison_button = Button(self.results_window, text="Clear Comparison Data", command=self.clear_comparison_data)
        clear_comparison_button.pack()

    def save_results(self, v0, angle, height, size, weight, distance, max_height, speed_at_end, time_step):
        filename = "simulation_results.csv"
        file_exists = os.path.isfile(filename)

        with open(filename, "a") as file:
            if not file_exists:
                file.write("Simulation,Timestamp,Speed,Angle,Height,Size,Weight,Distance,Max Height,End Speed,Time Step\n")

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            file.write(f"{self.simulation_count + 1},{timestamp},{v0:.2f},{angle:.2f},{height:.2f},{size:.2f},{weight:.2f},{distance:.2f},{max_height:.2f},{speed_at_end:.2f},{time_step:.3f}\n")

    def load_results(self):
        filename = "simulation_results.csv"
        try:
            with open(filename, "r") as file:
                next(file)
                for line in file:
                    values = line.strip().split(",")
                    self.tree.insert("", END, values=values)
        except FileNotFoundError:
            print("No previous results found.")
        except Exception as e:
            print(f"Error loading results: {e}")

    def view_previous_results(self):
        self.previous_results_window = Toplevel(self.root)
        self.previous_results_window.title("Previous Results")

        self.tree_previous = ttk.Treeview(self.previous_results_window, columns=(
            "Simulation", "Timestamp", "Speed", "Angle", "Height", "Size", "Weight", "Distance", "Max Height", "End Speed", "Time Step"
        ), show="headings")

        self.tree_previous.heading("Simulation", text="Simulation #")
        self.tree_previous.heading("Timestamp", text="Timestamp")
        self.tree_previous.heading("Speed", text="Speed (m/s)")
        self.tree_previous.heading("Angle", text="Angle (deg)")
        self.tree_previous.heading("Height", text="Height (m)")
        self.tree_previous.heading("Size", text="Size (m^2)")
        self.tree_previous.heading("Weight", text="Weight (kg)")
        self.tree_previous.heading("Distance", text="Distance (m)")
        self.tree_previous.heading("Max Height", text="Max Height (m)")
        self.tree_previous.heading("End Speed", text="End Speed (m/s)")
        self.tree_previous.heading("Time Step", text="Time Step (s)")

        self.tree_previous.pack(padx=10, pady=10)

        filename = "simulation_results.csv"
        try:
            with open(filename, "r") as file:
                next(file)
                for line in file:
                    values = line.strip().split(",")
                    self.tree_previous.insert("", END, values=values)
        except FileNotFoundError:
            print("No previous results found.")
        except Exception as e:
            print(f"Error loading results: {e}")

    def clear_comparison_data(self):
        self.comparison_projectiles = []
        self.ax.clear()
        self.ax.set_xlabel('Horizontal Distance (m)')
        self.ax.set_ylabel('Height (m)')
        self.ax.set_title('Projectile Trajectory with Atmosphere')
        self.ax.grid(True)
        plt.draw()

if __name__ == "__main__":
    root = Tk()
    app = SimulationApp(root)
    root.mainloop()
