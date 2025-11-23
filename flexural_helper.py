import numpy as np
import matplotlib.pyplot as plt

# Functions for beam and load case 1
def get_beam_and_load_inputs_2(weight,length,shift):
    point_loads = [(weight/(3.35*2),shift),(weight/(3.35*2),176+shift),(weight/(3.35*2),340+shift),(weight/(3.35*2),516+shift),(weight*1.35/(3.35*2),680+shift),(weight*1.35/(3.35*2),856+shift)]
    udl = []
    return length, point_loads, udl

# Functions for beam and load case 2
def get_beam_and_load_inputs_1(weight,length,shift):
    point_loads = [(weight/(6),shift),(weight/(6),176+shift),(weight/(6),340+shift),(weight/(6),516+shift),(weight/(6),680+shift),(weight/6,856+shift)]
    udl = []
    return length, point_loads, udl

# Get inputs for cross-section
def cross_section_inputs():
    num_rectangles = int(input("Enter the number of rectangles in the cross-section: "))
    rectangles = []
    for i in range(num_rectangles):
        print(f"\n--- Rectangle {i+1} ---")
        width = float(input(f"Enter the width of rectangle {i+1}: "))
        height = float(input(f"Enter the height of rectangle {i+1}: "))
        x_left = float(input(f"Enter the distance from the left edge for rectangle {i+1}: "))
        y_bottom = float(input(f"Enter the distance of the bottom edge of rectangle {i+1} from the bottom of the cross-section (assume bottom is zero): "))
        rectangles.append({'width': width, 'height': height, 'x_left': x_left, 'y_bottom': y_bottom})

    return rectangles

# Calculate centroid and second moment of area
def centroid_and_secondmoment(rectangles):
    total_area = 0
    area_moment_sum = 0
   
    # Finding centroid
    for rectangle in rectangles:
        area = rectangle['width'] * rectangle['height']
        total_area += area
        centroid_local = rectangle['y_bottom'] + rectangle['height'] / 2
        area_moment_sum += area * centroid_local
       
    centroid = area_moment_sum / total_area
    
    # Finding I
    totalI = 0
    for rectangle in rectangles:
        area = rectangle['width'] * rectangle['height']
        centroid_local = rectangle['y_bottom'] + rectangle['height'] / 2
        Ic = (rectangle['width'] * rectangle['height']**3) / 12
        d = centroid_local - centroid
       
        totalI += Ic + area * d**2

    min_y = min(rectangle['y_bottom'] for rectangle in rectangles)
    max_y = max(rectangle['y_bottom'] + rectangle['height'] for rectangle in rectangles)
    max_height = max_y - min_y
       
    return centroid, totalI, max_height

# Calculate reactions at supports
def calculate_reactions(length, point_loads, udl):
    moment_about_left = 0
    total_force = 0
   
    for magnitude, location in point_loads:
        moment_about_left += magnitude * location
        total_force += magnitude
       
    for magnitude, start, end in udl:
        force = magnitude * (end - start)
        total_force += force
        location = (start + end) / 2
        moment_about_left += force * location
    
    rightreaction = moment_about_left / length
    leftreaction = total_force - rightreaction
    return leftreaction, rightreaction

# Calculate shear force along the beam
def shear_force(length, point_loads, udl, leftreaction):
    x = np.linspace(0, length, 1250)
    V = np.zeros_like(x)
   
    point_loads_with_reactions = [(-leftreaction, 0)] + point_loads

    # Find shear at each position along the beam
    for i, pos in enumerate(x):
        shear = 0
        for magnitude, location in point_loads_with_reactions:
            if pos > location:
                shear += magnitude
       
        for magnitude, start, end in udl:
            if pos > start:
                effective_end = min(pos, end)
                shear += magnitude * (effective_end - start)
        V[i] = -shear
    return x, V

# Calculate bending moment along the beam
def bending_moment(x, V):
    M = np.zeros_like(x)
    for i in range(1, len(x)):
        # Since every pieces of the shear diagram is linear between points, we can use trapezoidal integration to find moment
        M[i] = M[i-1] + np.trapezoid(V[i-1:i+1], x[i-1:i+1])
    return x, M

# Calculate factor of safety for compression and tension
def factor_of_safety(max_moment, I, height, c, yield_strength_comp, yield_strength_tens): 
    if I == 0:
        return float('inf')
    
    max_stress_comp = (abs(max_moment) * c) / I
    max_stress_tens = (abs(max_moment) * c) / I


    if max_moment>=0:
        max_stress_comp = (abs(max_moment) * (height-c)) / I
    else:
        max_stress_tens = (abs(max_moment) * (height-c)) / I
    

    try:
        factor_of_safety_comp = yield_strength_comp / abs(max_stress_comp)
    except:
        factor_of_safety_comp=float('inf')

    try:
        factor_of_safety_tens = yield_strength_tens / abs(max_stress_tens)
    except:
        factor_of_safety_tens=float('inf')
    
    return factor_of_safety_comp,factor_of_safety_tens

# Create a diagram of cross-section
def plot_cross_section(rectangles):
    fig, ax = plt.subplots()
    for rect in rectangles:
        ax.add_patch(
            plt.Rectangle((rect['x_left'], rect['y_bottom']), rect['width'], rect['height'],
                          fill=True, edgecolor='black', alpha=0.5)
        )
    all_rights = [r['x_left'] + r['width'] for r in rectangles]
    all_tops = [r['y_bottom'] + r['height'] for r in rectangles]
    max_w = max(all_rights)
    max_h = max(all_tops)
    ax.set_xlim(0, max_w * 1.1)
    ax.set_ylim(0, max_h * 1.1)
    ax.set_aspect('equal')
    plt.xlabel('Width (from left)')
    plt.ylabel('Height (from bottom)')
    plt.title('Cross Section')
    plt.show()

# Load Case 2
def main2(weight, length, shift,rectangles, yield_strength_comp, yield_strength_tens, I, c, height):    
    length, point_loads, udl = get_beam_and_load_inputs_2(weight, length, shift)
   
    leftreaction, rightreaction = calculate_reactions(length, point_loads, udl)
    x_shear, V = shear_force(length, point_loads, udl, leftreaction)
    x_moment, M = bending_moment(x_shear, V)
   
    max_shear_force = max(abs(V))
    max_abs_moment_pos = M[M > 0].max() if np.any(M > 0) else 0
    max_abs_moment_neg = M[M < 0].max() if np.any(M < 0) else 0

    fos_c_pos, fos_t_pos = factor_of_safety(abs(max_abs_moment_pos), I, height, c, yield_strength_comp, yield_strength_tens)
    fos_c_neg, fos_t_neg = factor_of_safety(abs(max_abs_moment_neg), I, height, c, yield_strength_comp, yield_strength_tens)
   
    return f"{shift}\t{leftreaction:.2f}\t{rightreaction:.2f}\t{min(fos_c_pos,fos_c_neg):.2f}\t{min(fos_t_pos,fos_t_neg):.2f}\n",max_shear_force,max(max_abs_moment_pos,max_abs_moment_neg)

# Load Case 1
def main1(weight, length, shift,rectangles, yield_strength_comp, yield_strength_tens, I, c, height):    
    length, point_loads, udl = get_beam_and_load_inputs_1(weight, length, shift)
   
    leftreaction, rightreaction = calculate_reactions(length, point_loads, udl)
    x_shear, V = shear_force(length, point_loads, udl, leftreaction)
    x_moment, M = bending_moment(x_shear, V)
   
    max_shear_force = max(abs(V))
    max_abs_moment_pos = M[M > 0].max() if np.any(M > 0) else 0
    max_abs_moment_neg = M[M < 0].max() if np.any(M < 0) else 0

    fos_c_pos, fos_t_pos = factor_of_safety(abs(max_abs_moment_pos), I, height, c, yield_strength_comp, yield_strength_tens)
    fos_c_neg, fos_t_neg = factor_of_safety(abs(max_abs_moment_neg), I, height, c, yield_strength_comp, yield_strength_tens)
   
    return f"{shift}\t{leftreaction:.2f}\t{rightreaction:.2f}\t{min(fos_c_pos,fos_c_neg):.2f}\t{min(fos_t_pos,fos_t_neg):.2f}\n",max_shear_force,max(max_abs_moment_pos,max_abs_moment_neg)