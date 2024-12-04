import math
import numpy as np
import matplotlib.pyplot as plt

def odometry_calculation(L, r, n1, n2, N):
    # Mittlere Strecke
    s = 2 * math.pi * r * ((n1 + n2) / 2) * (1 / N)
    
    # Rotationswinkel
    dTheta = (n2 - n1) * (2 * math.pi * r) / (N * L)
    
    # Winkelkorrektur
    if n2 > n1:  # Rechtsdrehung
        dTheta = -abs(dTheta)
    else:  # Linksdrehung
        dTheta = abs(dTheta)
    
    # X und Y Bewegung
    dx = s * math.cos(dTheta)
    dy = s * math.sin(dTheta)
    
    return dx, dTheta, dy

def draw_robot_movement(L, r, n1, n2, N):
    # Berechnungen
    dx, dTheta, dy = odometry_calculation(L, r, n1, n2, N)
    
    plt.figure(figsize=(12, 8))
    
    # Startpunkt
    start_x, start_y = 0, 0
    
    # Endpunkt
    end_x, end_y = dx, dy
    
    def draw_wheel(x, y, wheel_offset, angle, is_left=True):
        wheel_width = r * 0.5
        wheel_length = r * 1.5
        
        rotation_matrix = np.array([
            [np.cos(angle), -np.sin(angle)],
            [np.sin(angle), np.cos(angle)]
        ])
        
        wheel_corners = np.array([
            [-wheel_length/2, -wheel_width/2],
            [wheel_length/2, -wheel_width/2],
            [wheel_length/2, wheel_width/2],
            [-wheel_length/2, wheel_width/2]
        ])
        
        # Rotiere und verschiebe in x und y
        rotated_corners = np.dot(wheel_corners, rotation_matrix.T)
        rotated_corners += [x + wheel_offset * math.cos(angle + math.pi/2), 
                             y + wheel_offset * math.sin(angle + math.pi/2)]
        
        color = 'blue' if is_left else 'green'
        plt.fill(rotated_corners[:, 0], rotated_corners[:, 1], color=color, alpha=0.5)
    
    # Start-Räder
    draw_wheel(start_x, start_y, L/2, 0, is_left=True)   # Linkes Rad
    draw_wheel(start_x, start_y, -L/2, 0, is_left=False)  # Rechtes Rad
    
    # Bewegungspfad
    plt.plot([start_x, end_x], [start_y, end_y], 'ro-', label='Bewegungspfad')
    
    # End-Räder
    draw_wheel(end_x, end_y, L/2, dTheta, is_left=True)   # Linkes Rad
    draw_wheel(end_x, end_y, -L/2, dTheta, is_left=False)  # Rechtes Rad
    
    plt.title('2D Odometry Movement mit Rädern')
    plt.xlabel('X Position (cm)')
    plt.ylabel('Y Position (cm)')
    plt.grid(True)
    plt.axis('equal')
    plt.legend()
    
    plt.show()
    
    print(f"Delta x: {dx:.2f} cm")
    print(f"Delta Theta: {dTheta:.4f} rad")
    print(f"Delta y: {dy:.2f} cm")

# Parameter
L = 21   # Radabstand in cm
r = 2.4  # Radradius in cm
n1 = -50 # Encoder Links ticks
n2 = 1000 # Encoder Rechts ticks
N = 260  # Ticks für eine Umdrehung

# Aufruf der Visualisierungsfunktion
draw_robot_movement(L, r, n1, n2, N)