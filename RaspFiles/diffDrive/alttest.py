import RPi.GPIO as GPIO
import time
from pyPS4Controller.controller import Controller

# Motor-Pin-Setup
GPIO.setmode(GPIO.BCM)
AIN1 = 17  # Left motor forward
AIN2 = 18  # Left motor backward
BIN1 = 22  # Right motor forward
BIN2 = 23  # Right motor backward
GPIO.setwarnings(False)
GPIO.setup(AIN1, GPIO.OUT)
GPIO.setup(AIN2, GPIO.OUT)
GPIO.setup(BIN1, GPIO.OUT)
GPIO.setup(BIN2, GPIO.OUT)

# Initialize PWM on all pins
p1 = GPIO.PWM(AIN1, 50)
p2 = GPIO.PWM(AIN2, 50)
p3 = GPIO.PWM(BIN1, 50)
p4 = GPIO.PWM(BIN2, 50)
p1.start(0)
p2.start(0)
p3.start(0)
p4.start(0)

def map_value(value, in_min, in_max, out_min, out_max):
    """Map values from one range to another"""
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def set_motor_speeds(left_speed, right_speed):
    """
    Set the speed and direction for both motors
    Speed values should be between -100 and 100
    Negative values mean backward rotation
    """
    # Left motor
    if left_speed >= 0:
        p1.ChangeDutyCycle(0)
        p2.ChangeDutyCycle(min(abs(left_speed), 100))
    else:
        p1.ChangeDutyCycle(min(abs(left_speed), 100))
        p2.ChangeDutyCycle(0)
    
    # Right motor
    if right_speed >= 0:
        p3.ChangeDutyCycle(min(abs(right_speed), 100))
        p4.ChangeDutyCycle(0)
    else:
        p3.ChangeDutyCycle(0)
        p4.ChangeDutyCycle(min(abs(right_speed), 100))

# Bewegungsfunktionen
def stop():
    """Stop both motors"""
    p1.ChangeDutyCycle(0)
    p2.ChangeDutyCycle(0)
    p3.ChangeDutyCycle(0)
    p4.ChangeDutyCycle(0)

# Encoder setup remains the same
spin_count = 0
spin_count2 = 0
E1A = 20
E1B = 21
E2A = 27
E2B = 27
GPIO.setup(E1B, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(E1A, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(E2B, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(E2A, GPIO.IN, pull_up_down=GPIO.PUD_UP)

class MyController(Controller):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.forward_speed = 0
        self.turn_rate = 0
        self.max_speed = 50  # Default max speed
        self.speed_modifier = 1.0  # Modifier for slowing down with L2

    def on_L3_up(self, value):
        """Handle forward movement with proportional control"""
        self.forward_speed = map_value(value, -32767, 32767, self.max_speed, 0)
        print(f"Moving forward with speed: {self.forward_speed}")
        self._update_motors()
        
    def on_L3_down(self, value):
        """Handle backward movement with proportional control"""
        self.forward_speed = -map_value(value, -32767, 32767, 0, self.max_speed)
        print(f"Moving backward with speed: {self.forward_speed}")
        self._update_motors()
        
    def on_L3_left(self, value):
        """Handle left turning with proportional control"""
        self.turn_rate = -map_value(value, -32767, 32767, -1, 1)
        self._update_motors()
        
    def on_L3_right(self, value):
        """Handle right turning with proportional control"""
        self.turn_rate = -map_value(value, -32767, 32767, -1, 1)
        self._update_motors()
        
    def on_L3_x_at_rest(self):
        """Reset turning when joystick is centered horizontally"""
        self.turn_rate = 0
        self._update_motors()
        
    def on_L3_y_at_rest(self):
        """Reset forward/backward speed when joystick is centered vertically"""
        self.forward_speed = 0
        self._update_motors()
        
    def on_L2_press(self, value):
        """Reduce the maximum speed proportionally when L2 is pressed"""
        #self.speed_modifier = map_value(value, 0, 255, 0.2, 1)  # Min speed modifier of 0.2
        if self.speed_modifier-0.01 < 0.1:
            print("speed mod at lowest")
        else:
            self.speed_modifier -= 0.01
            print(f"Reducing speed, modifier set to {self.speed_modifier:.2f}")
            self._update_motors()
        
    def on_L2_release(self):
        """Reset the speed modifier when L2 is released"""
        # self.speed_modifier = 1.0
        print("L2 released, speed modifier reset")
        self._update_motors()    

    def on_R2_press(self, value):
        """increase the maximum speed proportionally when R2 is pressed"""
        #self.speed_modifier = map_value(value, 0, 255, 0.2, 1)  # Min speed modifier of 0.2
        if self.speed_modifier+0.01 > 2:
            print("speed mod at highest")
        else:
            self.speed_modifier += 0.01
            print(f"increase speed, modifier set to {self.speed_modifier:.2f}")
            self._update_motors()
            
    def on_R2_release(self):
        """Reset the speed modifier when L2 is released"""
        # self.speed_modifier = 1.0
        print("L2 released, speed modifier reset")
        self._update_motors()

    def _update_motors(self):
        """Calculate and set motor speeds based on joystick position and speed modifier"""
        # Apply speed modifier
        adjusted_speed = self.forward_speed * self.speed_modifier
        print(f"Forward speed: {self.forward_speed};    speed mod: {self.speed_modifier}; real speed: {adjusted_speed}")
        # Calculate left and right motor speeds based on forward speed and turn rate

        if adjusted_speed == 0 and self.turn_rate == -1 or self.turn_rate == 1:
            left_speed = adjusted_speed * (1 + self.turn_rate)
            right_speed = adjusted_speed * (1 - self.turn_rate)
        else:
            left_speed = adjusted_speed * (1 + self.turn_rate)
            right_speed = adjusted_speed * (1 - self.turn_rate)

        print(f"turn_rate: {self.turn_rate}")
        print(f"right speed: {right_speed}")
        print(f"left speed: {left_speed}")

        # Scale speeds to max_speed while maintaining ratio
        max_speed = max(abs(left_speed), abs(right_speed))
        if max_speed > self.max_speed and max_speed > 0:
            if self.turn_rate == 1:
                left_speed = -48 * scale
                right_speed = 48 * scale
            elif self.turn_rate == -1:
                left_speed = 48 * scale
                right_speed = -48 * scale
            else:
                scale = self.max_speed / max_speed
                left_speed *= scale
                right_speed *= scale

        # Set motor speeds
        set_motor_speeds(left_speed, right_speed)
        #print(f"Left: {left_speed:.1f}, Right: {right_speed:.1f}, Turn rate: {self.turn_rate:.2f}")

# Create and start controller instance
controller = MyController(interface="/dev/input/js0", connecting_using_ds4drv=False)
controller.listen()
