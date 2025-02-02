import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import art3d
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk, ImageDraw
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import cv2
from dataclasses import dataclass
import json
from typing import Optional

# Weapon Database Classes
@dataclass
class Weapon:
    id: int
    name: str
    type: str
    velocity_mult: float
    spread_factor: float
    pattern_desc: str
    stain_chars: str
    satellite_chance: float
    caliber: Optional[str] = None
    blade_length: Optional[float] = None

class WeaponDB:
    def __init__(self, file_path='weapons.json'):
        self.weapons = []
        self.file_path = file_path
        self.load_weapons()

    def load_weapons(self):
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                self.weapons = [
                    Weapon(
                        id=w["id"],
                        name=w["name"],
                        type=w["type"],
                        velocity_mult=w["velocity_mult"],
                        spread_factor=w["spread_factor"],
                        pattern_desc=w["pattern_desc"],
                        stain_chars=w["stain_chars"],
                        satellite_chance=w["satellite_chance"],
                        caliber=w.get("caliber"),
                        blade_length=w.get("blade_length")
                    ) for w in data.get('weapons', [])
                ]
        except (FileNotFoundError, json.JSONDecodeError) as e:
            messagebox.showerror("Load Error", f"Failed to load weapons: {str(e)}")
            self.weapons = []

    def save_weapons(self):
        data = {"weapons": [{
            "id": w.id,
            "name": w.name,
            "type": w.type,
            "velocity_mult": w.velocity_mult,
            "spread_factor": w.spread_factor,
            "pattern_desc": w.pattern_desc,
            "stain_chars": w.stain_chars,
            "satellite_chance": w.satellite_chance,
            "caliber": w.caliber,
            "blade_length": w.blade_length
        } for w in self.weapons]}
        try:
            with open(self.file_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save weapons: {str(e)}")

    def get_weapon(self, name):
        return next((w for w in self.weapons if w.name == name), None)

    def get_all_weapons(self):
        return [w.name for w in self.weapons]

# Weapon Manager GUI
class WeaponManager(tk.Toplevel):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.title("Weapon Database Manager")
        self.db = db
        self.geometry("400x300")
        self.listbox = tk.Listbox(self)
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.refresh_list()
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Add", command=self.add_weapon).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Refresh", command=self.refresh_list).pack(side=tk.LEFT, padx=5)

    def refresh_list(self):
        self.db.load_weapons()
        self.listbox.delete(0, tk.END)
        for weapon in self.db.weapons:
            self.listbox.insert(tk.END, weapon.name)

    def add_weapon(self):
        AddWeaponDialog(self, self.db)
        self.refresh_list()

class AddWeaponDialog(tk.Toplevel):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.title("Add New Weapon")
        self.geometry("300x400")
        self.vars = {}
        fields = [
            ("Name", "name", tk.StringVar()),
            ("Type", "type", tk.StringVar()),
            ("Velocity Multiplier", "velocity_mult", tk.DoubleVar(value=1.0)),
            ("Spread Factor", "spread_factor", tk.DoubleVar(value=0.1)),
            ("Satellite Chance", "satellite_chance", tk.DoubleVar(value=0.2)),
            ("Pattern Description", "pattern_desc", tk.StringVar()),
            ("Stain Characteristics", "stain_chars", tk.StringVar())
        ]
        for i, (label, field, var) in enumerate(fields):
            tk.Label(self, text=label).grid(row=i, column=0, padx=5, pady=5, sticky=tk.W)
            tk.Entry(self, textvariable=var).grid(row=i, column=1, padx=5, pady=5)
            self.vars[field] = var
        tk.Button(self, text="Save", command=self.save_weapon).grid(row=len(fields), columnspan=2, pady=10)

    def save_weapon(self):
        try:
            new_id = max(w.id for w in self.db.weapons) + 1 if self.db.weapons else 1
            new_weapon = Weapon(
                id=new_id,
                name=self.vars["name"].get(),
                type=self.vars["type"].get(),
                velocity_mult=self.vars["velocity_mult"].get(),
                spread_factor=self.vars["spread_factor"].get(),
                satellite_chance=self.vars["satellite_chance"].get(),
                pattern_desc=self.vars["pattern_desc"].get(),
                stain_chars=self.vars["stain_chars"].get()
            )
            self.db.weapons.append(new_weapon)
            self.db.save_weapons()
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid value: {str(e)}")

# Stabbing Simulation Classes
class HumanBody3D:
    def __init__(self, ax):
        self.ax = ax
        self.body_parts = {}
        self.create_body()

    def create_body(self):
        torso_height = 1.8
        torso_radius = 0.3
        self.body_parts['torso'] = self.add_cylinder(
            pos=(0, 0, 0),
            radius=torso_radius,
            height=torso_height,
            color='peachpuff'
        )

        head_radius = 0.25
        self.body_parts['head'] = self.add_sphere(
            pos=(0, 0, torso_height + head_radius * 0.9),
            radius=head_radius,
            color='peachpuff'
        )

        arm_length = 0.8
        self.body_parts['left_arm'] = self.add_cylinder(
            pos=(-torso_radius, 0, torso_height * 0.7),
            radius=0.08,
            height=arm_length,
            direction=(1, 0, 0),
            color='peachpuff'
        )
        self.body_parts['right_arm'] = self.add_cylinder(
            pos=(torso_radius, 0, torso_height * 0.7),
            radius=0.08,
            height=arm_length,
            direction=(-1, 0, 0),
            color='peachpuff'
        )

    def add_cylinder(self, pos, radius, height, color, direction=(0, 0, 1)):
        u = np.linspace(0, 2 * np.pi, 50)
        z = np.linspace(0, height, 2)
        U, Z = np.meshgrid(u, z)
        X = radius * np.cos(U) + pos[0]
        Y = radius * np.sin(U) + pos[1]
        Z = Z + pos[2]

        if direction != (0, 0, 1):
            direction = np.array(direction) / np.linalg.norm(direction)
            rot_matrix = self.rotation_matrix((0, 0, 1), direction)
            points = np.vstack((X.ravel(), Y.ravel(), Z.ravel()))
            rotated_points = np.dot(rot_matrix, points).reshape(X.shape + (3,))
            X, Y, Z = rotated_points[..., 0], rotated_points[..., 1], rotated_points[..., 2]

        return self.ax.plot_surface(X, Y, Z, color=color, alpha=0.8)

    def add_sphere(self, pos, radius, color):
        u = np.linspace(0, 2 * np.pi, 50)
        v = np.linspace(0, np.pi, 50)
        x = radius * np.outer(np.cos(u), np.sin(v)) + pos[0]
        y = radius * np.outer(np.sin(u), np.sin(v)) + pos[1]
        z = radius * np.outer(np.ones(np.size(u)), np.cos(v)) + pos[2]
        return self.ax.plot_surface(x, y, z, color=color, alpha=0.8)

    @staticmethod
    def rotation_matrix(vector1, vector2):
        v = np.cross(vector1, vector2)
        c = np.dot(vector1, vector2)
        s = np.linalg.norm(v)
        if s == 0:
            return np.eye(3)
        kmat = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
        return np.eye(3) + kmat + np.dot(kmat, kmat) * ((1 - c) / (s ** 2))

class StabbingSimulation:
    def __init__(self, parent):
        self.parent = parent
        self.fig = plt.figure(figsize=(8, 6))
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        control_frame = tk.Frame(parent)
        control_frame.pack(pady=10)

        tk.Label(control_frame, text="Attack Angle (°):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.angle_var = tk.DoubleVar(value=45)
        tk.Scale(control_frame, variable=self.angle_var, from_=0, to=90, orient=tk.HORIZONTAL).grid(row=0, column=1, padx=5, pady=5)

        tk.Button(control_frame, text="Start Simulation", command=self.start_animation).grid(row=1, column=0, columnspan=2, pady=5)
        tk.Button(control_frame, text="Reset", command=self.reset_scene).grid(row=2, column=0, columnspan=2, pady=5)

        self.body = HumanBody3D(self.ax)
        self.initialize_blade()
        self.ax.set_xlim(-1, 1)
        self.ax.set_ylim(-1, 1)
        self.ax.set_zlim(0, 2)

    def initialize_blade(self):
        blade_length = 0.4
        blade_width = 0.05
        x = np.array([0, blade_length, blade_length, 0])
        y = np.array([-blade_width / 2, -blade_width / 2, blade_width / 2, blade_width / 2])
        z = np.zeros(4)

        verts = [list(zip(x, y, z))]
        self.blade = art3d.Poly3DCollection(verts)
        self.blade.set_color('silver')
        self.ax.add_collection3d(self.blade)

        self.blade_pos = np.array([0.5, 0, 1.2])

    def update_blade(self, progress):
        angle = np.radians(self.angle_var.get())
        attack_vector = np.array([
            np.cos(angle) * progress,
            0,
            -np.sin(angle) * progress
        ])

        new_verts = []
        for vert in self.blade.get_verts():
            translated_vert = np.array(vert) + self.blade_pos + attack_vector
            new_verts.append(translated_vert)
        self.blade.set_verts(new_verts)

    def animate_stab(self, frame=0):
        if self.animation_running:
            progress = np.sin(frame * 0.1)
            self.update_blade(progress)
            self.canvas.draw()
            self.parent.after(50, self.animate_stab, frame + 1)

    def start_animation(self):
        if not self.animation_running:
            self.animation_running = True
            self.animate_stab()

    def reset_scene(self):
        self.ax.cla()
        self.body = HumanBody3D(self.ax)
        self.initialize_blade()
        self.ax.set_xlim(-1, 1)
        self.ax.set_ylim(-1, 1)
        self.ax.set_zlim(0, 2)
        self.canvas.draw()

# Blood Spatter App
class BloodSpatterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Advanced Blood Spatter Analyzer")
        self.geometry("1200x800")
        self.db = WeaponDB()

        # Control Panel
        control_frame = tk.Frame(self, bd=2, relief=tk.RIDGE)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # Weapon Selection
        tk.Label(control_frame, text="Weapon:").pack()
        self.weapon_var = tk.StringVar()
        self.weapon_dropdown = ttk.Combobox(control_frame, textvariable=self.weapon_var)
        self.weapon_dropdown.pack()

        # Surface Selection
        tk.Label(control_frame, text="Surface:").pack()
        self.surface_var = tk.StringVar()
        surfaces = ["Smooth", "Rough", "Fabric"]
        ttk.Combobox(control_frame, textvariable=self.surface_var, values=surfaces).pack()

        # Parameters
        tk.Label(control_frame, text="Velocity (m/s):").pack()
        self.velocity_scale = tk.Scale(control_frame, from_=5, to=50, orient=tk.HORIZONTAL)
        self.velocity_scale.set(20)
        self.velocity_scale.pack()

        tk.Label(control_frame, text="Angle (°):").pack()
        self.angle_scale = tk.Scale(control_frame, from_=0, to=90, orient=tk.HORIZONTAL)
        self.angle_scale.set(45)
        self.angle_scale.pack()

        # Buttons
        tk.Button(control_frame, text="Run Simulation", command=self.run_simulation).pack(pady=10)
        tk.Button(control_frame, text="Upload Image", command=self.upload_image).pack(pady=5)
        tk.Button(control_frame, text="Generate Report", command=self.generate_report).pack(pady=5)
        tk.Button(control_frame, text="Manage Weapons", command=self.manage_weapons).pack(pady=5)

        # Visualization
        vis_frame = tk.Frame(self)
        vis_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

        self.fig_3d = plt.figure(figsize=(8, 6))
        self.ax_3d = self.fig_3d.add_subplot(111, projection='3d')
        self.canvas_3d = FigureCanvasTkAgg(self.fig_3d, master=vis_frame)
        self.canvas_3d.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.fig_2d, self.ax_2d = plt.subplots(figsize=(8, 4))
        self.canvas_2d = FigureCanvasTkAgg(self.fig_2d, master=vis_frame)
        self.canvas_2d.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.refresh_weapons()
        self.surface_var.set("Smooth")

        # Add Stabbing Simulation Tab
        self.add_stabbing_simulation_tab()

    def add_stabbing_simulation_tab(self):
        tab_control = ttk.Notebook(self)
        analysis_tab = ttk.Frame(tab_control)
        stabbing_tab = ttk.Frame(tab_control)
        tab_control.add(analysis_tab, text="Blood Analysis")
        tab_control.add(stabbing_tab, text="Stabbing Simulation")
        tab_control.pack(expand=1, fill="both")

        # Initialize stabbing simulation
        self.stabbing_sim = StabbingSimulation(stabbing_tab)

    def refresh_weapons(self):
        self.db.load_weapons()
        self.weapon_dropdown['values'] = self.db.get_all_weapons()
        if self.db.weapons:
            self.weapon_var.set(self.db.weapons[0].name)

    def manage_weapons(self):
        WeaponManager(self, self.db)
        self.refresh_weapons()

    def run_simulation(self):
        velocity = self.velocity_scale.get()
        angle = self.angle_scale.get()
        surface = self.surface_var.get()
        weapon = self.weapon_var.get()
        x, y, z = simulate_blood_spatter(velocity, angle, surface, weapon, self.db)
        if not x:
            return

        # Update 3D plot
        self.ax_3d.clear()
        self.ax_3d.scatter(x, y, z, c='r', marker='.', alpha=0.6)
        self.ax_3d.set_xlabel("X Distance (m)")
        self.ax_3d.set_ylabel("Y Distance (m)")
        self.ax_3d.set_zlabel("Z Deviation (m)")
        self.canvas_3d.draw()

        # Update 2D plot
        self.ax_2d.clear()
        self.ax_2d.scatter(x, y, c='r', marker='.', alpha=0.6)
        self.ax_2d.set_xlabel("X Distance (m)")
        self.ax_2d.set_ylabel("Y Distance (m)")
        self.canvas_2d.draw()

    def upload_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            try:
                self.img = Image.open(file_path)
                self.tk_img = ImageTk.PhotoImage(self.img)
                # Implement image display logic here
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {str(e)}")

    def generate_report(self):
        pass

def simulate_blood_spatter(velocity, angle_degrees, surface_type, weapon, db, num_droplets=100):
    weapon_data = db.get_weapon(weapon)
    if not weapon_data:
        messagebox.showerror("Error", "Selected weapon not found in database")
        return [], [], []

    velocity *= weapon_data.velocity_mult
    spread = weapon_data.spread_factor * {
        "Smooth": 0.5,
        "Rough": 2.0,
        "Fabric": 1.2
    }.get(surface_type, 1.0)

    angle_radians = np.radians(angle_degrees)
    gravity = 9.81
    time_of_flight = (2 * velocity * np.sin(angle_radians)) / gravity
    x, y, z = [], [], []

    for _ in range(num_droplets):
        t = np.random.uniform(0, time_of_flight)
        xi = velocity * np.cos(angle_radians) * t
        yi = velocity * np.sin(angle_radians) * t - 0.5 * gravity * t**2
        zi = np.random.normal(0, 0.1)
        xi += np.random.normal(0, spread)
        yi += np.random.normal(0, spread)
        x.append(xi)
        y.append(yi)
        z.append(zi)

        if np.random.rand() < weapon_data.satellite_chance:
            for _ in range(np.random.randint(1, 4)):
                x_sat = xi + np.random.normal(0, spread / 3)
                y_sat = yi + np.random.normal(0, spread / 3)
                z_sat = zi + np.random.normal(0, 0.05)
                x.append(x_sat)
                y.append(y_sat)
                z.append(z_sat)

    return x, y, z

if __name__ == "__main__":
    app = BloodSpatterApp()
    app.mainloop()
