from helper import *


WEIGHT=452.2
LENGTH=1200
TARGET_FOS=2.0

if __name__ == "__main__":
    rectangles, yield_strength_comp, yield_strength_tens = cross_section_inputs()

    plot_cross_section(rectangles)

    centroid_y, I, c, height = centroid_and_secondmoment(rectangles)

    print(f"\n\n\n\n\nFor the composite cross-section:")
    print(f"Overall centroidal y-axis: {centroid_y:.2f}")
    print(f"Second moment of area (I): {I:.2f}")
    print(f"Max distance from centroid to outer fiber (c): {c:.2f}")

    fos_tens_min=100000
    fos_comp_min=100000

    with open("data.txt", 'w') as f:
        f.write("Shift\tLeft Reaction\tRight Reaction\tFOS Comp.\tFOS Tens.\n")
        for i in range(344):
            string=main(WEIGHT,LENGTH,i,rectangles, yield_strength_comp, yield_strength_tens,centroid_y, I, c, height)
            f.write(string)
            string=string.split("\t")
            if float(string[3])<fos_comp_min:
                fos_comp_min=float(string[3])
            if float(string[4])<fos_tens_min:
                fos_tens_min=float(string[4])
        f.close()

    print(f"\nMinimum Factor of Safety in Compression over all load positions: {fos_comp_min}")
    print(f"Minimum Factor of Safety in Tension over all load positions: {fos_tens_min}")
    
    print("The maximum weight this design can carry is: " +str(WEIGHT*min(fos_comp_min/TARGET_FOS,fos_tens_min/TARGET_FOS)))

