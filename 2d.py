import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import cellpylib as cpl

# Define Custom Rule for 2D Cellular Automaton
class customrule(cpl.BaseRule):
    def __call__(self, n, c, t):
        center_cell = n[1][1]  # Center cell in the 3x3 neighborhood
        neighbor_sum = np.sum(n) - center_cell  # Sum of all neighbors (excluding center)

        if center_cell == 0:  # Dead cell
            return 1 if neighbor_sum == 3 else 0  # Becomes alive if exactly 3 neighbors
        else:  # Alive cell
            return 1 if neighbor_sum in [2, 3] else 0  # Survives if 2 or 3 neighbors

# ✅ Initialize a 60x60 2D Cellular Automaton
rows, cols = 60, 60
cellular_automaton = np.zeros((rows, cols), dtype=int)  # Ensure a NumPy array

# ✅ Insert Glider (at position 28,30)
glider = np.array([[0, 0, 1], [1, 0, 1], [0, 1, 1]])
cellular_automaton[28:31, 30:33] = glider  

# ✅ Insert Blinker (at position 40,15)
blinker = np.array([[1, 1, 1]])
cellular_automaton[40, 15:18] = blinker  

# ✅ Insert Lightweight Spaceship (at position 18,45)
lw_spaceship = np.array([[0, 1, 1, 1, 1], 
                         [1, 0, 0, 0, 1], 
                         [0, 0, 0, 1, 0], 
                         [1, 0, 0, 0, 1]])
cellular_automaton[18:22, 45:50] = lw_spaceship  

# ✅ Convert to 3D array before evolving
cellular_automaton = np.array([cellular_automaton])  

# ✅ Evolve the 2D Cellular Automaton
rule = customrule()  # Fixed instantiation
cellular_automaton = cpl.evolve2d(
    cellular_automaton, 
    timesteps=220, 
    neighbourhood='Moore',  
    apply_rule=rule, 
    memoize='recursive'
)

# ✅ Setup Animation
fig, ax = plt.subplots()
ax.set_xlim((0, 60))
ax.set_ylim((60, 0))
img = ax.imshow(cellular_automaton[0], interpolation='nearest', cmap='Greys')

# ✅ Animation functions
def init():
    img.set_data(cellular_automaton[0])
    return (img,)

def animate(i):
    img.set_data(cellular_automaton[i])
    return (img,)

# ✅ Run Animation
anim = animation.FuncAnimation(fig, animate, init_func=init, frames=220, interval=50, blit=True, repeat=False)
plt.show()
