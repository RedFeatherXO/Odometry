import pygame
import math

class RobotSimulation:
    def __init__(self, robot):
        self.robot = robot
        self.trajectory = [(0, 0, 0)]  # Liste von (x, y, theta)
        self.screen_size = (800, 600)
        self.scale = 100  # Maßstab für die Darstellung

    def simulate_movement(self, left_ticks, right_ticks):
        x, y, theta = self.robot.update_pose(left_ticks, right_ticks, 260)
        self.trajectory.append((x, y, theta))

    def draw_coordinate_system(self, screen, width, height):
        # Mitte des Fensters
        center_x = width // 2
        center_y = height // 2
        
        # Farben
        axis_color = (200, 200, 200)  # Grau
        marker_color = (150, 150, 150)  # Dunkleres Grau
        
        # Achsen zeichnen
        pygame.draw.line(screen, axis_color, (0, center_y), (width, center_y), 2)  # X-Achse
        pygame.draw.line(screen, axis_color, (center_x, 0), (center_x, height), 2)  # Y-Achse
        
        # Markierungen auf den Achsen
        marker_interval = 50  # Abstand zwischen den Markierungen in Pixeln
        font = pygame.font.Font(None, 20)  # Schriftart für Markierungen
        
        # X-Achse Markierungen
        for x in range(0, width, marker_interval):
            if x != center_x:  # Mitte nicht markieren
                pygame.draw.line(screen, marker_color, (x, center_y - 5), (x, center_y + 5), 1)
                label = font.render(str((x - center_x)/100), True, marker_color)
                screen.blit(label, (x - 10, center_y + 10))
        
        # Y-Achse Markierungen
        for y in range(0, height, marker_interval):
            if y != center_y:  # Mitte nicht markieren
                pygame.draw.line(screen, marker_color, (center_x - 5, y), (center_x + 5, y), 1)
                label = font.render(str((center_y - y)/100), True, marker_color)
                screen.blit(label, (center_x + 10, y - 10))

    def draw(self, screen,robot_color,linear_speed=0,angular_speed=0,drawText=False):

        # Letzte Position des Roboters
        x, y, theta = self.trajectory[-1]

        # Koordinaten skalieren und transformieren (für Bildschirmmitte)
        screen_x = self.screen_size[0] // 2 + int(x * self.scale)
        screen_y = self.screen_size[1] // 2 - int(y * self.scale)

        # Roboter als Kreis darstellen
        pygame.draw.circle(screen, robot_color, (screen_x, screen_y), 10)

        # Richtung anzeigen (als Linie)
        direction_x = screen_x + int(20 * math.cos(theta))
        direction_y = screen_y - int(20 * math.sin(theta))
        pygame.draw.line(screen, (255, 0, 0), (screen_x, screen_y), (direction_x, direction_y), 2)

        # Trajektorie zeichnen
        for i in range(len(self.trajectory) - 1):
            x1, y1, _ = self.trajectory[i]
            x2, y2, _ = self.trajectory[i + 1]

            screen_x1 = self.screen_size[0] // 2 + int(x1 * self.scale)
            screen_y1 = self.screen_size[1] // 2 - int(y1 * self.scale)
            screen_x2 = self.screen_size[0] // 2 + int(x2 * self.scale)
            screen_y2 = self.screen_size[1] // 2 - int(y2 * self.scale)

            pygame.draw.line(screen, (0, 255, 0), (screen_x1, screen_y1), (screen_x2, screen_y2), 2)

        if drawText:
            # Geschwindigkeit und Position anzeigen
            font = pygame.font.Font(None, 30)

            # Text anzeigen
            speed_text = f"Linear Speed: {linear_speed:.2f} m/s, Angular Speed: {angular_speed:.2f} rad/s"
            position_text = f"Position (X, Y, Theta): ({x:.2f}, {y:.2f}, {theta:.2f})"
            
            speed_surface = font.render(speed_text, True, (255, 255, 255))  # Weiß
            position_surface = font.render(position_text, True, (255, 255, 255))  # Weiß

            # Text auf dem Bildschirm anzeigen
            screen.blit(speed_surface, (10, 10))  # Geschwindigkeitsanzeige oben links
            screen.blit(position_surface, (10, 40))  # Positionsanzeige direkt darunter
