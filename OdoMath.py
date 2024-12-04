import math

L = 21 #Links und rechts Radabstand in cm
r = 2.4 #Radradius in cm
n1 = 100 #Encoder Links ticks 
n2 = 101 #Encoder Rechts ticks
N = 260 # Ticks for one revolution

dx = 2*math.pi*r*((n1+n2)/2)*(1/N)
dTheta = abs(n1-n2)*(2*math.pi*L)/N*2
dy = math.tan(dTheta)*dx