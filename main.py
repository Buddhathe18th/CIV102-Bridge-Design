from flexural_helper import *
from shear_helper import *
from buckle_helper import *

# Load Case 1 constraints
WEIGHT=400
LENGTH=1250

# Load Case 2 constraints
WEIGHT_2=452
LENGTH_2=1250

# General Constants
TARGET_FOS=2.0
YIELD_STRENGTH_COMP=6  #MPa
YIELD_STRENGTH_TENS=30  #MPa
SHEAR_YIELD_STRENGTH=4  #MPa
ELASTIC_MODULUS=4000  #MPa
POISSON_RATIO=0.2  #unitless


def area_used(rectangles):
    """Calculate the area of matboard used for this cross-section"""
    total_area = 0
    for rectangle in rectangles:
        side= rectangle['width']  if rectangle['height']==1.27 else rectangle['height']
        area = side*LENGTH
        total_area += area
    return total_area

if __name__ == "__main__":
    # Take inputs for cross-section
    rectangles = cross_section_inputs()

    fos=[]

    # Display cross-section
    plot_cross_section(rectangles)

    # Centroid and second moment of area calculation
    centroid_y, I, height = centroid_and_secondmoment(rectangles)

    fos_tens_min=100000
    fos_comp_min=100000
    max_shear_force=0
    max_moment=0
    with open("data.txt", 'w') as f:
        # File header
        f.write("Shift\tLeft Reaction\tRight Reaction\tFOS Comp.\tFOS Tens.\n")

        # For all positions of train over beam for each millimeter shift. Since the maximum shear and moment occur when the entire train is on the beam, we only need to consider shifts that place all axles on the beam.
        for i in range(344):
            string, shear_force,moment=main2(WEIGHT_2,LENGTH_2,i,rectangles, YIELD_STRENGTH_COMP, YIELD_STRENGTH_TENS, I, centroid_y, height)
            f.write(string)
            string=string.split("\t")
            
            # Update minimum FOS values and maximum shear/moment
            if float(string[3])<fos_comp_min:
                fos_comp_min=float(string[3])
            if float(string[4])<fos_tens_min:
                fos_tens_min=float(string[4])
            if shear_force>max_shear_force:
                max_shear_force=shear_force
            if moment>max_moment:
                max_moment=moment
        f.close()
    
    # Shear FOS calculation
    tau, height, Q_val, b_val, heights, Q, width_list=shear_fos(max_shear_force, rectangles, centroid_y, I)
    fos=[fos_comp_min,fos_tens_min,SHEAR_YIELD_STRENGTH/tau]

    # Buckling FOS calculation
    buckling=buckle(ELASTIC_MODULUS,POISSON_RATIO,I,max_moment,max_shear_force*Q_val/(I*b_val))
    fos=fos+buckling

    # Glue shear FOS calculation
    glue_fos=[]
    glue=int(input("How many glue shear cases to evaluate?: "))
    for i in range(glue):
        height=float(input("Height at which to evaluate glue shear FOS: "))
        glue_fos.append(glue_shear(rectangles,height,centroid_y,tau,max_shear_force,I))


    fos=fos+glue_fos

    # Output
    print(f"\n\n\n\n\nFor the composite cross-section:")
    print(f"Overall centroidal y-axis: {centroid_y:.2f}")
    print(f"Second moment of area (I): {I:.2f}")

    print("\n"*2+f"Minimum Factor of Safety in Compression over all load positions: {fos_comp_min}")
    print(f"Minimum Factor of Safety in Tension over all load positions: {fos_tens_min}")
    print(f"Minimum Factor of Safety in Shear over all load positions: {SHEAR_YIELD_STRENGTH/tau:.2f}")
    print(f"Minimum Factor of Safety in Glue Shear: {min(glue_fos):.2f}")

    
    print(f"Minimum Factor of Safety in Buckling over all load positions: {min(buckling)}")
    
    # Calculate ratios of FOS to target FOS
    ratios = [val / TARGET_FOS for val in fos]
    min_ratio = min(ratios)
    min_index = ratios.index(min_ratio)
    
    print(f"The maximum weight this design can carry is: {WEIGHT*min_ratio:.2f} for index {min_index}")

    print(f"The area used in this design is: {area_used(rectangles)} mm^2")

    print(fos)