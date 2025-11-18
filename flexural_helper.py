import numpy as np
import matplotlib.pyplot as plt

def get_beam_and_load_inputs(weight,length,shift):
    point_loads = [(weight/(3.35*2),shift),(weight/(3.35*2),176+shift),(weight/(3.35*2),340+shift),(weight/(3.35*2),516+shift),(weight*1.35/(3.35*2),680+shift),(weight*1.35/(3.35*2),856+shift)]
    
    # TODO: Self Weight
    udl = []
    # num_udl = int(input("Enter the number of uniformly distributed loads: "))
    # for i in range(num_udl):
    #     magnitude = float(input(f"Enter the magnitude of udl {i+1} (use negative for upward force): "))
    #     startloc = float(input(f"Enter the start location of udl {i+1} from the left end: "))
    #     endloc = float(input(f"Enter the end location of udl {i+1} from the left end: "))
    #     udl.append((magnitude, startloc, endloc))
       
    return length, point_loads, udl

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

def centroid_and_secondmoment(rectangles):
    total_area = 0
    area_moment_sum = 0
   
    for rectangle in rectangles:
        area = rectangle['width'] * rectangle['height']
        total_area += area
        centroid_local = rectangle['y_bottom'] + rectangle['height'] / 2
        area_moment_sum += area * centroid_local
       
    centroid = area_moment_sum / total_area
   
    totalI = 0
    for rectangle in rectangles:
        area = rectangle['width'] * rectangle['height']
        centroid_local = rectangle['y_bottom'] + rectangle['height'] / 2
        #I = bh^3/12
        Ic = (rectangle['width'] * rectangle['height']**3) / 12
        d = centroid_local - centroid
       
        totalI += Ic + area * d**2

    min_y = min(rectangle['y_bottom'] for rectangle in rectangles)
    max_y = max(rectangle['y_bottom'] + rectangle['height'] for rectangle in rectangles)
    max_height = max_y - min_y
       
    return centroid, totalI, max_height

def calculate_reactions(length, point_loads, udl):

    #Assumes a pin support at the left and a roller support at the right
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

     #Note that at static equilibrium, the sum of total moments around the left support beam is zero
     #This means that the the (sum of moments from all loads) -  (right reaction force * length) = zero  
     #Thus, the right reaction force is (total moment)/beam length.
    rightreaction = moment_about_left / length
   
    #Note that at static equilibrium, the sum of vertical forces is zero:
    #This means that the (left reaction force) + (right reaction force) - total force = 0
    #Thus, left reaction force is total force - right reaction force
    leftreaction = total_force - rightreaction
    return leftreaction, rightreaction

def shear_force(length, point_loads, udl, leftreaction):
    x = np.linspace(0, length, 1000)
    V = np.zeros_like(x)
   
    point_loads_with_reactions = [(-leftreaction, 0)] + point_loads

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

def bending_moment(x, V):
    """Calculates the bending moment by integrating the shear force."""
    M = np.zeros_like(x)
    for i in range(1, len(x)):
        M[i] = M[i-1] + np.trapezoid(V[i-1:i+1], x[i-1:i+1])
    return x, M

def factor_of_safety(max_moment, I, height, c, yield_strength_comp, yield_strength_tens):
    """Calculates the factor of safety."""
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

# def shear_fos()

def main(weight, length, shift,rectangles, yield_strength_comp, yield_strength_tens, I, c, height):    
    length, point_loads, udl = get_beam_and_load_inputs(weight, length, shift)
   
    leftreaction, rightreaction = calculate_reactions(length, point_loads, udl)
    x_shear, V = shear_force(length, point_loads, udl, leftreaction)
    x_moment, M = bending_moment(x_shear, V)
   
    
    max_shear_force = max(abs(V))
    max_abs_moment_pos = M[M > 0].max() if np.any(M > 0) else None
    max_abs_moment_neg = M[M < 0].max() if np.any(M < 0) else None



    fos_c_pos, fos_t_pos = factor_of_safety(abs(max_abs_moment_pos), I, height, c, yield_strength_comp, yield_strength_tens)
    fos_c_neg, fos_t_neg = factor_of_safety(abs(max_abs_moment_neg), I, height, c, yield_strength_comp, yield_strength_tens)

   
    # print("\n--- Analysis Results ---")
    # print(f"Reaction force at the left support: {leftreaction:.2f}")
    # print(f"Reaction force at the right support: {rightreaction:.2f}")
    
    # print(f"Maximum absolute bending moment: {max(max_abs_moment_pos,max_abs_moment_neg):.2f}")
    # print(f"Factor of Safety for Compression: {min(fos_c_pos,fos_c_neg):.2f}")
    # print(f"Factor of Safety for Tension: {min(fos_t_pos,fos_t_neg):.2f}")
   
    return f"{shift}\t{leftreaction:.2f}\t{rightreaction:.2f}\t{min(fos_c_pos,fos_c_neg):.2f}\t{min(fos_t_pos,fos_t_neg):.2f}\n",max_shear_force,max(max_abs_moment_pos,max_abs_moment_neg)
    # Plot diagrams
    # plot_diagram(x_shear, V, "Shear Force Diagram", "Shear Force")
    # plot_diagram(x_moment, M, "Bending Moment Diagram", "Bending Moment")

if __name__ == "__main__":
    print("Please note that it is crucial to enter all lengths in milimeters (mm) and all force magnitudes in Newtons to ensure correct calculation.")
    main()