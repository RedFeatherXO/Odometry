import RPi.GPIO as GPIO
import time
from simple_pid import PID  # Falls nicht installiert: pip install simple-pid

# Motor Pins
AIN1 = 17
AIN2 = 18
BIN1 = 22
BIN2 = 23

class MotorControl:
    def __init__(self):
        self.running = True
        self.motor_power1 = 0
        self.motor_power2 = 0
        self.p1 = None
        self.p2 = None
        self.p3 = None
        self.p4 = None
        self.setup_gpio()

    def setup_gpio(self):
        # Motor Pins Setup
        GPIO.setup(AIN1, GPIO.OUT)
        GPIO.setup(AIN2, GPIO.OUT)
        GPIO.setup(BIN1, GPIO.OUT)
        GPIO.setup(BIN2, GPIO.OUT)
        
        # PWM Objekte erstellen
        self.p1 = GPIO.PWM(AIN1, 50)
        self.p2 = GPIO.PWM(AIN2, 50)
        self.p3 = GPIO.PWM(BIN1, 50)
        self.p4 = GPIO.PWM(BIN2, 50)
        
        # PWM starten
        self.p1.start(0)
        self.p2.start(0)
        self.p3.start(0)
        self.p4.start(0)

    def set_motor_speed(self, power1, power2):
        # Vorwärtsrichtung
        self.p1.ChangeDutyCycle(0)
        self.p2.ChangeDutyCycle(power1)
        self.p3.ChangeDutyCycle(0)
        self.p4.ChangeDutyCycle(power2)

    def stop_motors(self):
        self.p1.ChangeDutyCycle(0)
        self.p2.ChangeDutyCycle(0)
        self.p3.ChangeDutyCycle(0)
        self.p4.ChangeDutyCycle(0)