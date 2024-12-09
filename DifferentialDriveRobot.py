import numpy as np
import math


class DifferentialDriveRobot:
    def __init__(self, wheel_radius, wheel_distance):
        self.x = 0.0      # Globale X-Position
        self.y = 0.0      # Globale Y-Position
        self.theta = 0.0  # Globale Orientierung
        
        self.r = wheel_radius      # Radradius
        self.L = wheel_distance    # Radabstand
    
    def update_pose(self, left_ticks, right_ticks, ticks_per_revolution):
        # Odometry-Berechnungen
        dx, dtheta, dy = self.calculate_odometry(left_ticks, right_ticks, ticks_per_revolution)
        
        # Globale Poses aktualisieren
        self.x += dx * math.cos(self.theta) - dy * math.sin(self.theta)
        self.y += dx * math.sin(self.theta) + dy * math.cos(self.theta)
        self.theta += dtheta
    
        return self.x, self.y, self.theta
    
    def calculate_odometry(self, n1, n2, N):
        # Mittlere Strecke
        s = 2 * math.pi * self.r * ((n1 + n2) / 2) * (1 / N)
        
        # Rotationswinkel
        dtheta = (n2 - n1) * (2 * math.pi * self.r) / (N * self.L)
        
        # X und Y Bewegung
        dx = s * math.cos(dtheta)
        dy = s * math.sin(dtheta)
        
        return dx, dtheta, dy