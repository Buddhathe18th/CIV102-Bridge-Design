import math

def buckle(E,poisson,I,current_moment):
    case=input("case: ")
    fos=[]
    while case!="STOP":
        case=int(case)
        t=float(input("thickness: "))
        b=float(input("width: "))
        if case==4:
            a=float(input("length: "))
        else:
            y=float(input("Furthest distance from centroid to part in interest: "))

        if case==1:
            max_moment=4*math.pi**2*E*I*t**2/(b**2*12*(1-poisson**2)*y)
            fos.append(max_moment/current_moment)
        elif case==2:
            max_moment=0.425*math.pi**2*E*I*t**2/(b**2*12*(1-poisson**2)*y)
            fos.append(max_moment/current_moment)
        elif case==3:
            max_moment=6*math.pi**2*E*I*t**2/(b**2*12*(1-poisson**2)*y)
            fos.append(max_moment/current_moment)
        elif case==4:
            tau=5*math.pi**2*E/(12*(1-poisson**2))* ((t/b)**2 +(t/a)**2)
            print(tau)
        case=input("case: ")
    return fos
# buckle(4000,0.2,587*10**3)