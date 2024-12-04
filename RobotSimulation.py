import matplotlib.pyplot as plt
import math

class RobotSimulation:
    def __init__(self, robot):
        self.robot = robot
        self.trajectory_x = [0]
        self.trajectory_y = [0]
        self.trajectory_theta = [0]
    
    def simulate_movement(self, encoder_data):
        for left_ticks, right_ticks in encoder_data:
            x, y, theta = self.robot.update_pose(left_ticks, right_ticks, 260)
            self.trajectory_x.append(x)
            self.trajectory_y.append(y)
            self.trajectory_theta.append(theta)
    
    def plot_trajectory(self):
        plt.figure(figsize=(12, 8))
        
        # Trajektorie
        plt.plot(self.trajectory_x, self.trajectory_y, 'ro-', label='Roboter Pfad')
        
        # Räder für jeden Punkt zeichnen
        for i in range(len(self.trajectory_x)):
            x = self.trajectory_x[i]
            y = self.trajectory_y[i]
            theta = self.trajectory_theta[i]
            
            # Linkes Rad
            left_wheel_x = x + self.robot.L/2 * math.cos(theta + math.pi/2)
            left_wheel_y = y + self.robot.L/2 * math.sin(theta + math.pi/2)
            
            # Rechtes Rad
            right_wheel_x = x - self.robot.L/2 * math.cos(theta + math.pi/2)
            right_wheel_y = y - self.robot.L/2 * math.sin(theta + math.pi/2)
            
            # Räder zeichnen
            plt.plot(left_wheel_x, left_wheel_y, 'bo', markersize=5)  # Linkes Rad (blau)
            plt.plot(right_wheel_x, right_wheel_y, 'go', markersize=5)  # Rechtes Rad (grün)
        
        plt.title('Roboter Trajektorie mit Rädern')
        plt.xlabel('X Position')
        plt.ylabel('Y Position')
        plt.grid(True)
        plt.axis('equal')
        plt.legend()
        plt.draw()
        plt.pause(0.001)