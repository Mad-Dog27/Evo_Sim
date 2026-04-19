import numpy as np
import matplotlib.pyplot as plt

# -----------------------------
# World dimensions (your request)
# -----------------------------
x = np.linspace(0, 800, 300)
y = np.linspace(0, 600, 300)
x, y = np.meshgrid(x, y)

# -----------------------------
# Terrain equation (same idea, scaled for large domain)
# -----------------------------
# Center of your 800x600 map
cx, cy = 400, 300
dist = np.sqrt((x - cx)**2 + (y - cy)**2)

# 1. Ripple effect: multiple peaks/lows radiating from center
# 2. Gaussian mask: suppresses values as they get further from the center (sigma=200)
# 3. Base noise: adds subtle variety to the hills
z = (2.5 * np.sin(0.05 * dist) * np.exp(-(dist**2) / (2 * 200**2)) + 
     0.5 * np.sin(0.02 * x) * np.cos(0.02 * y))


# -----------------------------
# Plot
# -----------------------------
fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(111, projection='3d')

surf = ax.plot_surface(x, y, z, cmap='terrain', linewidth=0)

# Labels
ax.set_title("800x600 Procedural Terrain")
ax.set_xlabel("X (0–800)")
ax.set_ylabel("Y (0–600)")
ax.set_zlabel("Height (Z)")

# Let Z auto-scale (important for peaks)
ax.autoscale(enable=True, axis='z')

# Better view angle
ax.view_init(elev=35, azim=45)

plt.show()