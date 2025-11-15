from helper import *


WEIGHT=452.2
LENGTH=1200

if __name__ == "__main__":
    rectangles, yield_strength_comp, yield_strength_tens = cross_section_inputs()
    centroid_y, I, c, height = centroid_and_secondmoment(rectangles)
    
    print(f"\nFor the composite cross-section:")
    print(f"Overall centroidal y-axis: {centroid_y:.2f}")
    print(f"Second moment of area (I): {I:.2f}")
    print(f"Max distance from centroid to outer fiber (c): {c:.2f}")

    with open("data.txt", 'w') as f:
        f.write("Shift\tLeft Reaction\tRight Reaction\tFOS Comp.\tFOS Tens.\n")
        for i in range(344):
            f.write(main(WEIGHT,LENGTH,i,rectangles, yield_strength_comp, yield_strength_tens,centroid_y, I, c, height))
        f.close()


