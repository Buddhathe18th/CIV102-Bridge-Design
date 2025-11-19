from flexural_helper import *
import matplotlib.pyplot as plt

def plot_Q_and_width(heights, Q, width_list):
    fig, ax1 = plt.subplots()

    color1 = 'tab:blue'
    ax1.set_xlabel('Height (mm)')
    ax1.set_ylabel('Q (mm³)', color=color1)
    ax1.plot(heights, Q, color=color1, label='Q (First Moment of Area)')
    ax1.tick_params(axis='y', labelcolor=color1)

    ax2 = ax1.twinx()  # Instantiate a second axes that shares the same x-axis
    color2 = 'tab:red'
    ax2.set_ylabel('Width (mm)', color=color2)
    ax2.plot(heights, width_list, color=color2, label='Width of Section')
    ax2.tick_params(axis='y', labelcolor=color2)

    plt.title('Q and Width vs. Cross Section Height')
    fig.tight_layout()  # Otherwise right y-label is slightly clipped
    plt.show()

def area_up_to_height(rectangles, h):
    """
    Calculates the total cross-sectional area from the bottom (y=0) up to height h.
    rectangles: list of dicts with keys 'width', 'height', 'x_left', 'y_bottom'
    h: the height up to which area is computed
    Returns: total area
    """
    total_area = 0
    for rect in rectangles:
        rect_top = rect['y_bottom'] + rect['height']
        rect_bottom = rect['y_bottom']
        # Only add area portion below height h
        if rect_bottom < h:
            # Find the height within the rectangle that is below h
            active_height = min(h, rect_top) - rect_bottom
            if active_height > 0:
                total_area += rect['width'] * active_height
    return total_area

def centroid_up_to_height(rectangles, h):
    """
    Calculates the centroid (y_bar) of area from y=0 up to height h.
    rectangles: list of dicts {'width', 'height', 'x_left', 'y_bottom'}
    h: height up to which area is considered
    Returns: centroid_y (distance from bottom to centroid of the area below h)
    """
    total_area = 0
    area_moment_sum = 0
    for rect in rectangles:
        rect_top = rect['y_bottom'] + rect['height']
        rect_bottom = rect['y_bottom']
        if rect_bottom < h:
            # Active height within [rect_bottom .. min(h, rect_top)]
            active_height = min(h, rect_top) - rect_bottom
            if active_height > 0:
                area = rect['width'] * active_height
                centroid_local = rect_bottom + active_height / 2
                total_area += area
                area_moment_sum += area * centroid_local
    if total_area == 0:
        return None  # or 0, if preferred
    centroid_y = area_moment_sum / total_area
    return centroid_y

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

    total_width=min(total_width1,total_width2)

    max_shear=tau_max*I*total_width/Q
    print(f"Glue Shear at height {height}: {Q:.2f} {I:.2f} {total_width:.2f} {current_shear:.2f}")
    return max_shear/current_shear





def shear_fos(maximum_shear_force, rectangles, centroid_y, I):
    min_y = min(rect['y_bottom'] for rect in rectangles)
    max_y = max(rect['y_bottom'] + rect['height'] for rect in rectangles)
    
    heights = list(range(int(min_y), int(max_y) + 1))[1:-1]
    width_list = []
    
    for h in heights:
        total_width = 0
        for rect in rectangles:
            if rect['y_bottom'] <= h < rect['y_bottom'] + rect['height']:
                total_width += rect['width']
        width_list.append(total_width)
    
    Q=[]

    for h in heights:
        area = area_up_to_height(rectangles, h)
        centroid = centroid_up_to_height(rectangles, h)
        Q.append(area * abs(centroid - centroid_y))
    
    tau=0
    Q_val=0
    b_val=0
    height=0

    for i in range(len(heights)):
        temp_tau= maximum_shear_force * Q[i] / (I * width_list[i]) if width_list[i]>0 else 0
        if temp_tau>tau:
            tau=temp_tau
            Q_val=Q[i]
            b_val=width_list[i]
            height=heights[i]

    return tau, height, Q_val, b_val, heights, Q, width_list


# rectangles, yield_strength_comp, yield_strength_tens = cross_section_inputs()
# centroid_y, I, height = centroid_and_secondmoment(rectangles)
# tau, height, Q_val, b_val, heights, Q, width_list=shear_fos(1508/2, rectangles, centroid_y, I)
# print(tau,height, Q_val,b_val)
# print(width_list)
# plot_Q_and_width(heights, Q, width_list)