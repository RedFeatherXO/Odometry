import pygame
import time
import math
from DifferentialDriveRobot import DifferentialDriveRobot
from RobotSimulationPyGame import RobotSimulation

# Roboter initialisieren
robot = DifferentialDriveRobot(wheel_radius=0.05, wheel_distance=0.21)
simulation = RobotSimulation(robot)

# Pygame initialisieren
pygame.init()
pygame.joystick.init()

def wait_for_controller():
    print("Warte auf Controller-Verbindung...")
    while pygame.joystick.get_count() == 0:
        pygame.joystick.quit()
        pygame.joystick.init()
        time.sleep(1)
    print("Controller gefunden!")

# Auf Controller warten
wait_for_controller()
joystick = pygame.joystick.Joystick(0)
joystick.init()

# Pygame Fenster öffnen
screen = pygame.display.set_mode(simulation.screen_size)
pygame.display.set_caption("Robot Simulation")

# Simulationsparameter
running = True
clock = pygame.time.Clock()
dt = 0.1  # Simulationsschritt in Sekunden
DEADZONE = 0.1  # Wert zwischen 0 und 1, unter dem Bewegungen ignoriert werden

print(joystick.get_numaxes()-1)

try:
    while running:
        screen.fill((0, 0, 0))  # Hintergrund schwarz

        # Koordinatensystem zeichnen
        simulation.draw_coordinate_system(screen,800, 600)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        pygame.event.pump()
        # Joystick-Werte auslesen
        left_stick_y = joystick.get_axis(1)  # Vertikale Achse des linken Sticks
        right_stick_x = joystick.get_axis(0)  # Horizontale Achse des rechten Sticks

        # Deadzone anwenden
        if abs(left_stick_y) < DEADZONE:
            left_stick_y = 0
        if abs(right_stick_x) < DEADZONE:
            right_stick_x = 0

        # Controller-Eingaben lesen
        linear_speed = -1*left_stick_y # -0.5  # Negative Richtung invertieren
        angular_speed = -1*right_stick_x #* 1.0

        # Encoder-Ticks berechnen
        wheel_circumference = 2 * math.pi * robot.r  # Umfang des Rades
        left_wheel_speed = linear_speed - angular_speed * (robot.L / 2)
        right_wheel_speed = linear_speed + angular_speed * (robot.L / 2)

        # Geschwindigkeit in Ticks umwandeln
        left_ticks = int((left_wheel_speed * dt * 260 / wheel_circumference))
        right_ticks = int((right_wheel_speed * dt * 260 / wheel_circumference))
        #print(f"left_ticks: {left_ticks}")
        # Bewegung simulieren
        simulation.simulate_movement(left_ticks, right_ticks)

        # Simulation zeichnen
        simulation.draw(screen,(0,0,255),linear_speed,angular_speed,True)

        pygame.display.flip()
        # Framerate steuern
        clock.tick(30)

except KeyboardInterrupt:
    print("Simulation beendet")
finally:
    pygame.quit()