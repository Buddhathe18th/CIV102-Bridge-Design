from flexural_helper import *
from shear_helper import *
from buckle_helper import *

WEIGHT=452.2
LENGTH=1200
TARGET_FOS=2.0
YIELD_STRENGTH_COMP=6  #MPa
YIELD_STRENGTH_TENS=30  #MPa
SHEAR_YIELD_STRENGTH=4  #MPa
ELASTIC_MODULUS=4000  #MPa
POISSON_RATIO=0.2  #unitless

if __name__ == "__main__":
    rectangles = cross_section_inputs()
    fos=[]
    plot_cross_section(rectangles)

    centroid_y, I, height = centroid_and_secondmoment(rectangles)

   

    fos_tens_min=100000
    fos_comp_min=100000
    max_shear_force=0
    max_moment=0
    with open("data.txt", 'w') as f:
        f.write("Shift\tLeft Reaction\tRight Reaction\tFOS Comp.\tFOS Tens.\n")
        for i in range(344):
            string, shear_force,moment=main(WEIGHT,LENGTH,i,rectangles, YIELD_STRENGTH_COMP, YIELD_STRENGTH_TENS, I, centroid_y, height)
            f.write(string)
            string=string.split("\t")
            if float(string[3])<fos_comp_min:
                fos_comp_min=float(string[3])
            if float(string[4])<fos_tens_min:
                fos_tens_min=float(string[4])
            if shear_force>max_shear_force:
                max_shear_force=shear_force
            if moment>max_moment:
                max_moment=moment
        f.close()
    
    tau, height, Q_val, b_val, heights, Q, width_list=shear_fos(max_shear_force, rectangles, centroid_y, I)
    fos=[fos_comp_min,fos_tens_min,SHEAR_YIELD_STRENGTH/tau]
    buckling=buckle(ELASTIC_MODULUS,POISSON_RATIO,I,max_moment,max_shear_force*Q_val/(I*b_val))
    fos=fos+buckling

    print(f"\n\n\n\n\nFor the composite cross-section:")
    print(f"Overall centroidal y-axis: {centroid_y:.2f}")
    print(f"Second moment of area (I): {I:.2f}")

    print("\n"*2+f"Minimum Factor of Safety in Compression over all load positions: {fos_comp_min}")
    print(f"Minimum Factor of Safety in Tension over all load positions: {fos_tens_min}")
    print(f"Minimum Factor of Safety in Shear over all load positions: {SHEAR_YIELD_STRENGTH/tau:.2f}")

    
    print(f"Minimum Factor of Safety in Buckling over all load positions: {min(buckling)}")
    ratios = [val / TARGET_FOS for val in fos]
    min_ratio = min(ratios)
    min_index = ratios.index(min_ratio)
    
    print("The maximum weight this design can carry is: " +str(WEIGHT*min_ratio)+" for index ",min_index)
    print(fos,tau)


