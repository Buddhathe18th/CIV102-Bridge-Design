import flexural_helper
import matplotlib.pyplot as plt
import numpy as np

# Load Case constraints
WEIGHT = 452
LENGTH = 1200

# General Constants
TARGET_FOS = 2.0
YIELD_STRENGTH_COMP = 6      # MPa
YIELD_STRENGTH_TENS = 30     # MPa
SHEAR_YIELD_STRENGTH = 4     # MPa
ELASTIC_MODULUS = 4000       # MPa
POISSON_RATIO = 0.2          # unitless

# FOS from main.py calculations
MIN_SAFETY_FACTOR = 2.49

# Getting load case point loads
def get_beam_and_load_inputs(weight, length, shift):
    point_loads = [(weight/(3.35*2),shift),(weight/(3.35*2),176+shift),(weight/(3.35*2),340+shift),(weight/(3.35*2),516+shift),(weight*1.35/(3.35*2),680+shift),(weight*1.35/(3.35*2),856+shift)]
    udl = []  # UDLS can be added here if needed
    return length, point_loads, udl

# Calculate shear force at each position
def shear_force(length, point_loads, udl=[], n_points=LENGTH):
    x = np.linspace(0, length, n_points)
    V = np.zeros_like(x)

    # Ignore loads outside beam length, when simulating train rolling onto/off beam
    filtered_loads = [(f, d) for f, d in point_loads if 0 <= d <= length]

    # Calulate reaction forces from moments and vertical forces
    total_force = sum(f for f, _ in filtered_loads)
    moment_sum = sum(f * d for f, d in filtered_loads)
    left_reaction = (total_force * length - moment_sum) / length

    for i, xi in enumerate(x):
        # Initialize shear with left reaction
        shear = left_reaction

        # For each point load to the left of xi, subtract its force
        for force, pos in filtered_loads:
            if xi >= pos:
                shear -= force

        # Subtract UDLS to the left
        for magnitude, start, end in udl:
            if xi >= start:
                effective_end = min(xi, end)
                shear -= magnitude * (effective_end - start)
        V[i] = shear
    return x, V

# Calculate bending moment at each position
def bending_moment(x, V):
    M = np.zeros_like(x)
    for i in range(1, len(x)):
        # Since every pieces of the shear diagram is linear between points, we can use trapezoidal integration to find moment
        M[i] = M[i-1] + np.trapezoid(V[i-1:i+1], x[i-1:i+1])
    return x, M

# Envelope variables
n_points = LENGTH
max_shear = np.zeros(n_points)
max_moment_pos = np.zeros(n_points)
max_moment_neg = np.zeros(n_points)
all_shears = []

# Calculate envelopes over all shifts, considering only when the entire train is on the beam
for shift in range(LENGTH-855):
    length, point_loads, udl = get_beam_and_load_inputs(WEIGHT, LENGTH, shift)
    x_shear, V = shear_force(length, point_loads, udl, n_points=n_points)
    x_moment, M = bending_moment(x_shear, V)

    # Envelope for shear force
    for j in range(len(V)):
        if abs(V[j]) > abs(max_shear[j]):
            max_shear[j] = abs(V[j])
    
    # Envelope for moment
    for j in range(len(M)):
        if M[j] > max_moment_pos[j]:
            max_moment_pos[j] = M[j]
        if M[j] < max_moment_neg[j]:
            max_moment_neg[j] = M[j]

# Plotting results
plt.figure()
plt.plot(x_shear, [moment*MIN_SAFETY_FACTOR for moment in max_moment_pos], label='Max Positive Moment')
plt.xlabel('Beam Position')
plt.ylabel('Value')
plt.legend()
plt.savefig("moments.png")
plt.show()

plt.figure()
plt.plot([abs(shear)*MIN_SAFETY_FACTOR for shear in max_shear], label='Enveloped Shear', color='red', linewidth=2)
plt.xlabel('Beam Position')
plt.ylabel('Shear Force')
plt.legend()
plt.savefig("shear_forces.png")
plt.show()

# Output maximum values
print("Maximum Moment:", max(max_moment_pos))
print("Maximum Shear (absolute):", max(abs(x) for x in max_shear))
