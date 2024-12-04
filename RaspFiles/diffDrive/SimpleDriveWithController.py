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
def forward(speed):
    p1.ChangeDutyCycle(0)
    p2.ChangeDutyCycle(speed)
    p3.ChangeDutyCycle(0)
    p4.ChangeDutyCycle(speed)

def backward(speed):
    p1.ChangeDutyCycle(speed)
    p2.ChangeDutyCycle(0)
    p3.ChangeDutyCycle(speed)
    p4.ChangeDutyCycle(0)


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

def my_callback(channel):
    global spin_count
    if not GPIO.input(E1B):
        spin_count += 1
    elif GPIO.input(E1B):
        spin_count -= 1

def my_callback2(channel):
    global spin_count2
    if not GPIO.input(E2B):
        spin_count2 += 1
    elif GPIO.input(E2B):
        spin_count2 -= 1

GPIO.add_event_detect(E1A, GPIO.RISING, callback=my_callback)
GPIO.add_event_detect(E2A, GPIO.RISING, callback=my_callback2)

class MyController(Controller):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.forward_speed = 0
        self.backward = False
        self.turn_rate = 0
        self.max_speed = 100
        self.deadzone = 10  # Ignore very small joystick movements
        
    def on_L3_up(self, value):
        """Handle forward movement with proportional control"""
        self.backward = False
        self.forward_speed = -map_value(value, -32767, 32767, 0, self.max_speed)
        print(f"Forward speed: {self.forward_speed}     value: {value}      max_speed: {self.max_speed}")
        self._update_motors()
        
    def on_L3_down(self, value):
        """Handle backward movement with proportional control"""
        self.backward = True
        self.forward_speed = -map_value(value, -32767, 32767, 0, self.max_speed)
        self._update_motors()
        
    def on_L3_left(self, value):
        """Handle left turning with proportional control"""
        if abs(value) > 32767 * (self.deadzone / 100):
            self.turn_rate = -map_value(value, -32767, 32767, -1, 1)
            self._update_motors()
            
    def on_L3_right(self, value):
        """Handle right turning with proportional control"""
        if abs(value) > 32767 * (self.deadzone / 100):
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
        
    def on_R2_press(self, value):
        """Use R2 as a speed multiplier (like a boost)"""
        self.max_speed = map_value(value, 0, 255, 50, 100)
        self._update_motors()
        
    def on_R2_release(self):
        """Reset speed multiplier when R2 is released"""
        self.max_speed = 50
        self._update_motors()
        
    def _update_motors(self):
        """Calculate and set motor speeds based on joystick position"""
        # Calculate left and right motor speeds based on forward speed and turn rate
        left_speed = self.forward_speed * (1 - self.turn_rate)
        right_speed = self.forward_speed * (1 + self.turn_rate)
        
        # Scale speeds to max_speed while maintaining ratio
        max_speed = max(abs(left_speed), abs(right_speed))
        if max_speed > self.max_speed and max_speed > 0:
            scale = self.max_speed / max_speed
            left_speed *= scale
            right_speed *= scale
        elif max_speed <= 0:
            right_speed = 0
            left_speed = 0
            
        # Set motor speeds
        set_motor_speeds(left_speed, right_speed)
        print(f"Left: {left_speed:.1f}, Right: {right_speed:.1f}, Turn: {self.turn_rate:.2f}")

# Create and start controller instance
controller = MyController(interface="/dev/input/js0", connecting_using_ds4drv=False)
controller.listen()