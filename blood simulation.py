import tkinter as tk
from tkinter import filedialog, ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk, ImageDraw

# Function to simulate blood spatter based on surface type
def simulate_blood_spatter(velocity, angle_degrees, surface_type, num_droplets=100):
    angle_radians = np.radians(angle_degrees)
    gravity = 9.81
    time_of_flight = (2 * velocity * np.sin(angle_radians)) / gravity
    x = velocity * np.cos(angle_radians) * time_of_flight
    y = velocity * np.sin(angle_radians) * time_of_flight - 0.5 * gravity * time_of_flight**2

    # Adjust parameters based on surface type
    if surface_type == "Smooth":
        spread = 0.05
        satellite_chance = 0.1
    elif surface_type == "Rough":
        spread = 0.2
        satellite_chance = 0.5
    elif surface_type == "Fabric":
        spread = 0.1
        satellite_chance = 0.3
    else:
        spread = 0.1
        satellite_chance = 0.2

    # Simulate droplets
    x_values = []
    y_values = []
    for _ in range(num_droplets):
        xi = x + np.random.normal(0, spread)
        yi = y + np.random.normal(0, spread)
        if np.random.rand() < satellite_chance:
            for _ in range(np.random.randint(1, 3)):
                x_sat = xi + np.random.normal(0, spread/2)
                y_sat = yi + np.random.normal(0, spread/2)
                x_values.append(x_sat)
                y_values.append(y_sat)
        x_values.append(xi)
        y_values.append(yi)
    return x_values, y_values

# Function to analyze uploaded image (simulated blood detection)
def analyze_image(image_path):
    # Open image and convert to RGB
    image = Image.open(image_path).convert("RGB")
    width, height = image.size

    # Detect "blood-like" regions (red color thresholding)
    red_pixels = []
    for x in range(width):
        for y in range(height):
            r, g, b = image.getpixel((x, y))
            if r > 100 and g < 50 and b < 50:  # Simple red threshold
                red_pixels.append((x, y))

    # Count stains and calculate average size
    stain_count = len(red_pixels)
    avg_area = stain_count / (width * height) if stain_count > 0 else 0
    return stain_count, avg_area

# GUI Application
class BloodSpatterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Blood Spatter Analyzer")
        self.geometry("1000x600")

        # Surface type dropdown
        self.surface_label = tk.Label(self, text="Select Surface Type:")
        self.surface_label.pack(pady=5)
        self.surface_var = tk.StringVar()
        self.surface_dropdown = ttk.Combobox(self, textvariable=self.surface_var, 
                                           values=["Smooth", "Rough", "Fabric"])
        self.surface_dropdown.pack(pady=5)
        self.surface_dropdown.set("Smooth")

        # Upload image button
        self.upload_btn = tk.Button(self, text="Upload Image", command=self.upload_image)
        self.upload_btn.pack(pady=10)

        # Image display frame
        self.image_frame = tk.Frame(self)
        self.image_frame.pack(side=tk.LEFT, padx=10)

        # Simulation plot frame
        self.plot_frame = tk.Frame(self)
        self.plot_frame.pack(side=tk.RIGHT, padx=10)

    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if file_path:
            # Analyze image
            stain_count, avg_area = analyze_image(file_path)
            
            # Display image
            img = Image.open(file_path)
            img.thumbnail((300, 300))
            img_tk = ImageTk.PhotoImage(img)
            img_label = tk.Label(self.image_frame, image=img_tk)
            img_label.image = img_tk
            img_label.pack()

            # Display analysis results
            result_text = f"Stains Detected: {stain_count}\nAverage Stain Area: {avg_area:.2f} px²"
            result_label = tk.Label(self.image_frame, text=result_text)
            result_label.pack()

            # Simulate blood spatter based on surface type
            self.run_simulation()

    def run_simulation(self):
        # Simulate with default values (customize as needed)
        velocity = 10  # m/s
        angle = 45  # degrees
        surface_type = self.surface_var.get()
        x, y = simulate_blood_spatter(velocity, angle, surface_type)

        # Plot simulation
        fig, ax = plt.subplots(figsize=(5, 4))
        ax.scatter(x, y, color='red', s=10)
        ax.set_title(f"Simulated Spatter ({surface_type} Surface)")
        ax.set_xlabel("Distance (m)")
        ax.set_ylabel("Height (m)")
        ax.grid(True)

        # Embed plot in GUI
        for widget in self.plot_frame.winfo_children():
            widget.destroy()
        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()

if __name__ == "__main__":
    app = BloodSpatterApp()
    app.mainloop()
