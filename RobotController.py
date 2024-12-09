import RPi.GPIO as GPIO
import time

class RobotController:
    def __init__(self, robot):
        self.robot = robot
        
        # Encoder pin setup
        self.E1A = 20
        self.E1B = 21
        self.E2A = 27
        self.E2B = 27
        
        # Encoder counters
        self.spin_count = 0
        self.spin_count2 = 0
        
        # GPIO setup
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Setup encoder pins
        GPIO.setup(self.E1B, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.E1A, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.E2B, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.E2A, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        # Add event detection
        GPIO.add_event_detect(self.E1A, GPIO.RISING, callback=self.my_callback)
        GPIO.add_event_detect(self.E2A, GPIO.RISING, callback=self.my_callback2)
    
    def my_callback(self, channel):
        if not GPIO.input(self.E1B):
            self.spin_count += 1
        elif GPIO.input(self.E1B):
            self.spin_count -= 1
    
    def my_callback2(self, channel):
        if not GPIO.input(self.E2B):
            self.spin_count2 += 1
        elif GPIO.input(self.E2B):
            self.spin_count2 -= 1
    
    def getEncoderData(self):
        # Return current encoder counts and reset them
        left_ticks = self.spin_count
        right_ticks = self.spin_count2
        
        self.spin_count = 0
        self.spin_count2 = 0
        
        return right_ticks, left_ticks
    
    def cleanup(self):
        # Clean up GPIO when done
        GPIO.cleanup()