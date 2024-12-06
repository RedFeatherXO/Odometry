
import os
import pygame
import time
import math
from DifferentialDriveRobot import DifferentialDriveRobot
from RobotSimulationPyGame import RobotSimulation
from RobotController import RobotController
from MotorController import MotorControl

# Dummy-Video-Treiber aktivieren für SSH
os.environ["SDL_VIDEODRIVER"] = "x11"

# Roboter initialisieren
robot = DifferentialDriveRobot(wheel_radius=0.05, wheel_distance=0.21)
simulation = RobotSimulation(robot)

# Pygame initialisieren
pygame.init()

# Pygame-Fenster
screen = pygame.display.set_mode(simulation.screen_size)
pygame.display.set_caption("Robot Simulation")

running = True
clock = pygame.time.Clock()

try:
    while running:
        screen.fill((0, 0, 0))
        simulation.draw_coordinate_system(screen, 800, 600)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        pygame.display.flip()
        clock.tick(30)
except KeyboardInterrupt:
    print("Simulation beendet")
finally:
    pygame.quit()
