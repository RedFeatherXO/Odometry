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
        p1.ChangeDutyCycle(left_speed)  # Forward
        p2.ChangeDutyCycle(0)
    else:
        p1.ChangeDutyCycle(0)
        p2.ChangeDutyCycle(abs(left_speed))  # Backward
    
    # Right motor
    if right_speed >= 0:
        p3.ChangeDutyCycle(right_speed)  # Forward
        p4.ChangeDutyCycle(0)
    else:
        p3.ChangeDutyCycle(0)
        p4.ChangeDutyCycle(abs(right_speed))  # Backward

def stop():
    """Stop both motors"""
    set_motor_speeds(0, 0)

# Encoder setup
spin_count = 0
spin_count2 = 0
E1A = 20
E1B = 21
E2A = 27
E2B = 28
GPIO.setup(E1A, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(E1B, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(E2A, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(E2B, GPIO.IN, pull_up_down=GPIO.PUD_UP)

class MyController(Controller):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.forward_speed = 0
        self.turn_rate = 0
        self.max_speed = 50  # Default max speed
        self.turn_speed = 48  # Speed used for in-place turning
        self.speed_modifier = 1.0  # Modifier for speed adjustment
        self.min_speed_modifier = 0.1
        self.max_speed_modifier = 2.0

    def on_L3_up(self, value): #on_L3_up
        """Forward/backward control"""
        # Umgekehrte Zuordnung für intuitivere Steuerung
        self.forward_speed = map_value(value, -32767, 32767, self.max_speed, -self.max_speed)
        self._update_motors()
        
    def on_L3_down(self, value): #on_L3_down
        """Forward/backward control"""
        # Umgekehrte Zuordnung für intuitivere Steuerung
        self.forward_speed = map_value(value, -32767, 32767, self.max_speed, -self.max_speed)
        self._update_motors()
        
    def on_L3_left(self, value):#on_L3_left
        """Turning control"""
        # Umgekehrte Zuordnung für intuitivere Steuerung
        self.turn_rate = -map_value(value, -32767, 32767, -1, 1)
        self._update_motors()
        
    def on_L3_right(self, value):#on_L3_right
        """Turning control"""
        # Umgekehrte Zuordnung für intuitivere Steuerung
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
        """Reduce speed modifier"""
        new_modifier = max(self.speed_modifier - 0.01, self.min_speed_modifier)
        if new_modifier != self.speed_modifier:
            self.speed_modifier = new_modifier
            print(f"Speed modifier reduced to {self.speed_modifier:.2f}")
            self._update_motors()
        
    def on_R2_press(self, value):
        """Increase speed modifier"""
        new_modifier = min(self.speed_modifier + 0.01, self.max_speed_modifier)
        if new_modifier != self.speed_modifier:
            self.speed_modifier = new_modifier
            print(f"Speed modifier increased to {self.speed_modifier:.2f}")
            self._update_motors()

    def _update_motors(self):
        """Calculate and set motor speeds based on joystick position and speed modifier"""
        adjusted_speed = self.forward_speed * self.speed_modifier
        turn_speed = self.turn_speed * self.speed_modifier

        # Check if turn rate is at maximum for in-place turning
        if abs(self.turn_rate) >= 0.95:  # Using 0.95 to account for slight joystick variations
            # Drehen an Ort und Stelle
            if self.turn_rate > 0:  # Nach rechts drehen
                left_speed = turn_speed
                right_speed = -turn_speed
            else:  # Nach links drehen
                left_speed = -turn_speed
                right_speed = turn_speed
        else:
            # Normal driving with turning
            left_speed = adjusted_speed * (1 - self.turn_rate)
            right_speed = adjusted_speed * (1 + self.turn_rate)

        # Ensure speeds don't exceed maximumssssssss
        left_speed = max(min(left_speed, self.max_speed), -self.max_speed)
        right_speed = max(min(right_speed, self.max_speed), -self.max_speed)

        # Set motor speeds
        set_motor_speeds(left_speed, right_speed)
        print(f"Speeds - Left: {left_speed:.1f}, Right: {right_speed:.1f}, Turn: {self.turn_rate:.2f}")

try:
    # Create and start controller instance
    controller = MyController(interface="/dev/input/js0", connecting_using_ds4drv=False)
    controller.listen()
except KeyboardInterrupt:
    print("\nStopping robot...")
    stop()
    GPIO.cleanup()
except Exception as e:
    print(f"Error: {e}")
    stop()
    GPIO.cleanup()

#Update