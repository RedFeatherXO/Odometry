from DifferentialDriveRobot import DifferentialDriveRobot
from RobotSimulation import RobotSimulation

# Roboter initialisieren
robot = DifferentialDriveRobot(wheel_radius=0.05, wheel_distance=0.21)
simulation = RobotSimulation(robot)

# Beispiel-Encoder-Daten
encoder_data = [
    (100, 120),  # Erste Bewegung
    (150, 130),  # Zweite Bewegung
    (200, 180),   # Dritte Bewegung
    (150, 130),  # Zweite Bewegung
    (200, 180),   # Dritte Bewegung
    (150, 130),  # Zweite Bewegung
    (200, 180),   # Dritte Bewegung
    (150, 130),  # Zweite Bewegung
]

# Simulation durchführen
simulation.simulate_movement(encoder_data)
simulation.plot_trajectory()

#wie kann ich encoder daten simulieren wenn ich als input einen ps4 controller benutzen will um später den echten roboter zu kontrollieren