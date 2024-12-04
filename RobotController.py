class RobotController:
    def __init__(self, robot):
        self.robot = robot
    
    def go_straight(self, distance, speed):
        # Berechne benötigte Encoder-Ticks
        pass
    
    def turn(self, angle):
        # Drehe um einen bestimmten Winkel
        pass
    
    def follow_path(self, waypoints):
        # Folge einer Reihe von Wegpunkten
        pass


    def getEncoderData(self):
        right = 0
        left = 0
        return right,left