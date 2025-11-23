import flexural_helper
import matplotlib.pyplot as plt
import numpy as np

# --------- Constants ---------
WEIGHT = 400
LENGTH = 1200
TARGET_FOS = 2.0
YIELD_STRENGTH_COMP = 6      # MPa
YIELD_STRENGTH_TENS = 30     # MPa
SHEAR_YIELD_STRENGTH = 4     # MPa
ELASTIC_MODULUS = 4000       # MPa
POISSON_RATIO = 0.2          # unitless

MIN_SAFETY_FACTOR = 2.49

# --------- Beam and Load Generation ---------
def get_beam_and_load_inputs(weight, length, shift):
    single_load = weight / (3 * 2)
    positions = [shift, 176 + shift, 340 + shift, 516 + shift, 680 + shift, 856 + shift]
    point_loads = [(single_load, pos) for pos in positions]
    udl = []  # Add UDLs here if needed
    return length, point_loads, udl

def shear_force(length, point_loads, udl=[], n_points=LENGTH):
    """Calculate shear force at each position for given point and distributed loads."""
    x = np.linspace(0, length, n_points)
    V = np.zeros_like(x)

    # Filter loads within span
    filtered_loads = [(f, d) for f, d in point_loads if 0 <= d <= length]

    # Calculate reactions (simply supported beam)
    total_force = sum(f for f, _ in filtered_loads)
    moment_sum = sum(f * d for f, d in filtered_loads)
    left_reaction = (total_force * length - moment_sum) / length
    # Don't need right_reaction for shear (except for completeness)

    for i, xi in enumerate(x):
        shear = left_reaction
        # Subtract point loads to the left
        for force, pos in filtered_loads:
            if xi >= pos:
                shear -= force
        # Subtract distributed load to the left
        for magnitude, start, end in udl:
            if xi >= start:
                effective_end = min(xi, end)
                shear -= magnitude * (effective_end - start)
        V[i] = shear
    return x, V

def bending_moment(x, V):
    M = np.zeros_like(x)
    for i in range(1, len(x)):
        M[i] = M[i-1] + np.trapz(V[i-1:i+1], x[i-1:i+1])
    return x, M

# --------- Envelope Arrays ---------
n_points = LENGTH
max_shear = np.zeros(n_points)
max_moment_pos = np.zeros(n_points)
max_moment_neg = np.zeros(n_points)
all_shears = []

# --------- Envelope Calculation ---------
for shift in range(LENGTH-855):
    length, point_loads, udl = get_beam_and_load_inputs(WEIGHT, LENGTH, shift)
    x_shear, V = shear_force(length, point_loads, udl, n_points=n_points)
    x_moment, M = bending_moment(x_shear, V)

    # Absolute envelope for shear force
    for j in range(len(V)):
        if abs(V[j]) > abs(max_shear[j]):
            max_shear[j] = abs(V[j])
    # Positive envelope for moment
    for j in range(len(M)):
        if M[j] > max_moment_pos[j]:
            max_moment_pos[j] = M[j]
        if M[j] < max_moment_neg[j]:
            max_moment_neg[j] = M[j]

    all_shears.append(V)

# --------- Plotting ---------
plt.figure()
plt.plot(x_shear, [moment*MIN_SAFETY_FACTOR for moment in max_moment_pos], label='Max Positive Moment')
# plt.plot(x_shear, max_moment_neg, label='Max Negative Moment')
plt.xlabel('Beam Position')
plt.ylabel('Value')
plt.legend()
plt.savefig("moments.png")

plt.show()

# Overlay all individual shear curves (faint gray, for reference)
plt.figure()
# for V in all_shears:
#     plt.plot(x_shear, V, color='gray', alpha=0.2)
plt.plot([abs(shear)*MIN_SAFETY_FACTOR for shear in max_shear], label='Enveloped Shear', color='red', linewidth=2)
plt.xlabel('Beam Position')
plt.ylabel('Shear Force')
plt.legend()
plt.savefig("shear_forces.png")
plt.show()

print("Maximum Moment:", max(max_moment_pos))
print("Maximum Shear (absolute):", max(abs(x) for x in max_shear))
