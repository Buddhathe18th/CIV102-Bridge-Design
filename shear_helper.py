from flexural_helper import *
import matplotlib.pyplot as plt

# Finds the areaa up until a height of h of the cross section
def area_up_to_height(rectangles, h):
    total_area = 0
    for rect in rectangles:
        rect_top = rect['y_bottom'] + rect['height']
        rect_bottom = rect['y_bottom']
        # Only add area portion below height h
        if rect_bottom < h:
            active_height = min(h, rect_top) - rect_bottom
            if active_height > 0:
                total_area += rect['width'] * active_height
    return total_area

# Finds the centroid y-coordinate up until a height of h of the cross section
def centroid_up_to_height(rectangles, h):
    total_area = 0
    area_moment_sum = 0
    for rect in rectangles:
        rect_top = rect['y_bottom'] + rect['height']
        rect_bottom = rect['y_bottom']
        if rect_bottom < h:
            # Rectangle is within our height range
            active_height = min(h, rect_top) - rect_bottom
            if active_height > 0:
                area = rect['width'] * active_height
                centroid_local = rect_bottom + active_height / 2
                total_area += area
                area_moment_sum += area * centroid_local
    # Avoid division by zero
    if total_area == 0:
        return None
    centroid_y = area_moment_sum / total_area
    return centroid_y

# Calculates the glue shear factor of safety at a given height
def glue_shear(rectangles,height,centroid_y,tau_max,current_shear,I):
    Q=area_up_to_height(rectangles, height)*abs(centroid_up_to_height(rectangles, height) - centroid_y)
    total_width1 = 0
    total_width2 = 0
    for rect in rectangles:
        if rect['y_bottom'] <= height < rect['y_bottom'] + rect['height']:
            total_width1 += rect['width']

    for rect in rectangles:
        if rect['y_bottom'] <= height-1 < rect['y_bottom'] + rect['height']:
            total_width2 += rect['width']

    # Catches rounding errors in decimals
    total_width=min(total_width1,total_width2)

    max_shear=tau_max*I*total_width/Q
    print(f"Glue Shear at height {height}: {Q:.2f} {I:.2f} {total_width:.2f} {current_shear:.2f}")
    return max_shear/current_shear

# Calculates the maximum shear stress
def shear_fos(maximum_shear_force, rectangles, centroid_y, I):
    min_y = min(rect['y_bottom'] for rect in rectangles)
    max_y = max(rect['y_bottom'] + rect['height'] for rect in rectangles)
    
    # Ignore first and last edge heights
    heights = list(range(int(min_y), int(max_y) + 1))[1:-1]
    width_list = []
    
    # Calculate width at each height
    for h in heights:
        total_width = 0
        for rect in rectangles:
            if rect['y_bottom'] <= h < rect['y_bottom'] + rect['height']:
                total_width += rect['width']
        width_list.append(total_width)
    
    Q=[]

    # Calculate Q at each height
    for h in heights:
        area = area_up_to_height(rectangles, h)
        centroid = centroid_up_to_height(rectangles, h)
        Q.append(area * abs(centroid - centroid_y))
    
    tau=0
    Q_val=0
    b_val=0
    height=0

    # Interate through heights to find maximum shear stress
    for i in range(len(heights)):
        temp_tau= maximum_shear_force * Q[i] / (I * width_list[i]) if width_list[i]>0 else 0
        if temp_tau>tau:
            tau=temp_tau
            Q_val=Q[i]
            b_val=width_list[i]
            height=heights[i]

    return tau, height, Q_val, b_val, heights, Q, width_list