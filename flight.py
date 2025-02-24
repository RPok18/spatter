import numpy as np
import matplotlib.pyplot as plt
from tkinter import Tk, Label, Button, Entry, StringVar
import time

# Constants
C = 0.47  # Drag coefficient
rho = 1.225  # Air density (kg/m^3)
g = 9.81  # Gravity (m/s^2)

class Projectile:
    def __init__(self, v0, angle, height, size, weight):
        self.v0 = v0
        self.angle = np.deg2rad(angle)
        self.height = height
        self.size = size
        self.weight = weight
        self.cosa = np.cos(self.angle)
        self.sina = np.sin(self.angle)
        self.k = 0.5 * C * rho * self.size / self.weight
        self.vx = self.v0 * self.cosa
        self.vy = self.v0 * self.sina
        self.x = 0
        self.y = self.height
        self.t = 0
        self.on_ground = False

    def update(self, dt):
        if not self.on_ground:
            v = np.sqrt(self.vx**2 + self.vy**2)
            self.vx -= self.k * self.vx * v * dt
            self.vy -= (g + self.k * self.vy * v) * dt
            
            self.x += self.vx * dt
            self.y += self.vy * dt
            
            self.t += dt

            if self.y < 0:
                self.y = 0
                self.on_ground = True
                self.vx = 0
                self.vy = 0

class SimulationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Projectile Simulation")
        self.dt = 0.1  # Time step (s)
        
        # Input fields
        height_label = Label(root, text="Initial Height (m):")
        height_label.pack()
        self.height_entry = Entry(root)
        self.height_entry.pack()

        angle_label = Label(root, text="Launch Angle (degrees):")
        angle_label.pack()
        self.angle_entry = Entry(root)
        self.angle_entry.pack()

        speed_label = Label(root, text="Initial Speed (m/s):")
        speed_label.pack()
        self.speed_entry = Entry(root)
        self.speed_entry.pack()

        size_label = Label(root, text="Cross-sectional Area (m^2):")
        size_label.pack()
        self.size_entry = Entry(root)
        self.size_entry.pack()

        weight_label = Label(root, text="Mass (kg):")
        weight_label.pack()
        self.weight_entry = Entry(root)
        self.weight_entry.pack()

        # Label to display distance
        self.distance_label = Label(root, text="Distance: ")
        self.distance_label.pack()

        # Button to start simulation
        simulate_button = Button(root, text="Simulate", command=self.start_simulation)
        simulate_button.pack()

        # Plotting area
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.ax.set_xlabel('Horizontal Distance (m)')
        self.ax.set_ylabel('Height (m)')
        self.ax.set_title('Projectile Trajectory')
        self.ax.grid(True)
        plt.ion()  # Turn on interactive mode
        plt.show(block=False)  # Show plot without blocking

    def start_simulation(self):
        v0 = float(self.speed_entry.get())  # Initial speed (m/s)
        angle = float(self.angle_entry.get())  # Launch angle (degrees)
        height = float(self.height_entry.get())  # Initial height (m)
        size = float(self.size_entry.get())  # Cross-sectional area (m^2)
        weight = float(self.weight_entry.get())  # Mass (kg)

        self.projectile = Projectile(v0, angle, height, size, weight)
        self.x_values = [self.projectile.x]
        self.y_values = [self.projectile.y]

        self.update_plot()

    def update_plot(self):
        self.projectile.update(self.dt)
        self.x_values.append(self.projectile.x)
        self.y_values.append(self.projectile.y)
        
        # Update distance label
        self.distance_label['text'] = f"Distance: {self.projectile.x:.2f} m"
        
        self.ax.clear()
        self.ax.plot(self.x_values, self.y_values)
        self.ax.set_xlabel('Horizontal Distance (m)')
        self.ax.set_ylabel('Height (m)')
        self.ax.set_title('Projectile Trajectory')
        self.ax.grid(True)
        plt.draw()
        plt.pause(0.01)  # Update plot

        if not self.projectile.on_ground:
            self.root.after(int(self.dt * 1000), self.update_plot)  # Call update_plot after dt seconds

if __name__ == "__main__":
    root = Tk()
    app = SimulationApp(root)
    root.mainloop()
