import pygame
import time
import math
import threading
import queue
from DifferentialDriveRobot import DifferentialDriveRobot
from RobotSimulationPyGame import RobotSimulation
from RobotController import RobotController
from MotorController import MotorControl
from HeadMaster.Master_command_center import SocketServer
import os
import sys

# Globale Queue für Tick-Daten
tick_queue = queue.Queue()

class ThreadedSocketServer(SocketServer):
    def __init__(self, tick_queue):
        super().__init__()
        self.tick_queue = tick_queue
        self.daemon = True  # Thread wird beendet, wenn Hauptprogramm endet

    def _process_data(self, data):
        """
        Überschreibt die Datenverarbeitungsmethode, um Ticks in die Queue zu legen
        """
        try:
            left_ticks, right_ticks = map(int, data.split(","))
            # Ticks in die Queue legen
            self.tick_queue.put((left_ticks, right_ticks))
        except (ValueError, Exception) as e:
            print(f"Fehler bei Datenverarbeitung: {e}")

def get_ticks_from_queue(tick_queue):
    """
    Hilfsfunktion zum Abrufen der letzten Ticks aus der Queue
    """
    left_ticks, right_ticks = 0, 0
    while not tick_queue.empty():
        left_ticks, right_ticks = tick_queue.get()
    return right_ticks, left_ticks

# Roboter initialisieren
robot = DifferentialDriveRobot(wheel_radius=0.05, wheel_distance=0.21)
realRobot = DifferentialDriveRobot(wheel_radius=0.05, wheel_distance=0.21)
simulation = RobotSimulation(robot)
robController = RobotController(realRobot)
#motorController = MotorControl()
RealSim = RobotSimulation(realRobot)
socketServer = ThreadedSocketServer(tick_queue)
socketServer.start_server()

# Pygame initialisieren
pygame.init()
pygame.joystick.init()
#motorController.setup_gpio()
#motorController.set_motor_speed(50,50)

def wait_for_controller():
    print("Warte auf Controller-Verbindung...")
    while pygame.joystick.get_count() == 0:
        pygame.joystick.quit()
        pygame.joystick.init()
        time.sleep(1)
    print("Controller gefunden!")

def wait_for_x_button():
    print("Press X button to start the program...")
    waiting = True
    while waiting:
        for event in pygame.event.get():
            # print(f"Nutton Fpresemd: {event}")
            if event.type == pygame.JOYBUTTONDOWN:
                # Check for X button (typically index 0 or 1 depending on controller)
                # print(f"Nutton Fpresemd: {event.button}")
                if event.button == 0:  # PlayStation X button
                    print("X button pressed. Starting program...")
                    waiting = False
                    break
            elif event.type == pygame.QUIT:
                return False
        
        time.sleep(0.1)  # Prevent high CPU usage
    return True

try:
    # Auf Controller warten
    wait_for_controller()
    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    # Pygame Fenster öffnen
    screen = pygame.display.set_mode(simulation.screen_size)
    pygame.display.set_caption("Robot Simulation")

    if not wait_for_x_button():
        print("Program terminated.")
        pygame.quit()
        sys.exit()

except KeyboardInterrupt:
    print("Simulation beendet")
    socketServer.stop_server()
    pygame.quit()
    sys.exit()

# Simulationsparameter
running = True
clock = pygame.time.Clock()
dt = 0.1  # Simulationsschritt in Sekunden
DEADZONE = 0.1  # Wert zwischen 0 und 1, unter dem Bewegungen ignoriert werden
Last_LeftTicks = 0
Last_RightTicks = 0

#print(joystick.get_numaxes()-1)

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
        left_stick_y = joystick.get_axis(1)*-1  # Vertikale Achse des linken Sticks
        right_stick_x = joystick.get_axis(0)*-1  # Horizontale Achse des rechten Sticks

        # Deadzone anwenden
        if abs(left_stick_y) < DEADZONE:
            left_stick_y = 0
        if abs(right_stick_x) < DEADZONE:
            right_stick_x = 0

        # Controller-Eingaben lesen
        linear_speed = left_stick_y # -0.5  # Negative Richtung invertieren
        angular_speed = right_stick_x * 1.0

        # Encoder-Ticks berechnen
        wheel_circumference = 2 * math.pi * robot.r  # Umfang des Rades
        left_wheel_speed = linear_speed - angular_speed * (robot.L / 2)
        right_wheel_speed = linear_speed + angular_speed * (robot.L / 2)

        # Geschwindigkeit in Ticks umwandeln
        left_ticks = int((left_wheel_speed * dt * 260 / wheel_circumference))
        right_ticks = int((right_wheel_speed * dt * 260 / wheel_circumference))
         # Ticks von Socket-Server abrufen
        real_right_ticks, real_left_ticks = get_ticks_from_queue(tick_queue)
        
        real_right_ticks -= Last_RightTicks
        real_left_ticks  -= Last_LeftTicks

        Last_LeftTicks = real_left_ticks
        Last_RightTicks = real_right_ticks

        #print(f"left_ticks: {left_ticks}")
        # Bewegung simulieren
        simulation.simulate_movement(left_ticks, right_ticks)
        RealSim.simulate_movement(real_left_ticks,real_right_ticks)

        # Simulation zeichnen
        simulation.draw(screen,(0,0,255),linear_speed,angular_speed,True)
        RealSim.draw(screen,(0,255,255))

        print(f"Encoder left: {real_left_ticks}; Encoder right {real_right_ticks}; X: {RealSim.trajectory[0]}; Y: {RealSim.trajectory[1]}; w: {RealSim.trajectory[2]}")

        pygame.display.flip()
        # Framerate steuern
        clock.tick(30)

except KeyboardInterrupt:
    print("Simulation beendet")
finally:
    socketServer.stop_server()
    pygame.quit() 
