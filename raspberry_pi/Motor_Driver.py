import RPi.GPIO as GPIO
import time

class MotorDriver:

    def __init__(self,AIN1_Pin,AIN2_Pin,BIN1_Pin,BIN2_Pin):
        self.AIN1 = AIN1_Pin
        self.AIN2 = AIN2_Pin
        self.BIN1 = BIN1_Pin
        self.BIN2 = BIN2_Pin
        self.forward = False
        self.backward = False
        self.stop = False
        self.PWM_LEFT = 0
        self.PWM_RIGHT = 0
        self.PWM_AIN1 = None
        self.PWM_AIN2 = None
        self.PWM_BIN1 = None
        self.PWM_BIN2 = None
        self.setupGPIO()

    def setupGPIO(self):
        GPIO.setup(self.AIN1,GPIO.OUT)
        self.PWM_AIN1 = GPIO.PWM(self.AIN1, 50)
        self.PWM_AIN1.start(0)

        GPIO.setup(self.AIN2, GPIO.OUT)
        self.PWM_AIN2 = GPIO.PWM(self.AIN2,50)
        self.PWM_AIN2.start(0)

        GPIO.setup(self.BIN1,GPIO.OUT)
        self.PWM_BIN1 = GPIO.PWM(self.BIN1,50)
        self.PWM_BIN1.start(0)

        GPIO.setup(self.BIN2,GPIO.OUT)
        self.PWM_BIN2 = GPIO.PWM(self.BIN2,50)
        self.PWM_BIN2.start(0)

    def DriveForward(self):
        self.PWM_AIN1(0)
        self.PWM_AIN2(self.PWM_LEFT)
        self.PWM_BIN1(0)
        self.PWM_BIN2(self.PWM_RIGHT)

    def DriveBackward(self):

        self.PWM_AIN1(self.PWM_LEFT)
        self.PWM_AIN2(0)
        self.PWM_BIN1(self.PWM_RIGHT)
        self.PWM_BIN2(0)

    def DriveStop(self):
        self.PWM_AIN1(0)
        self.PWM_AIN2(0)
        self.PWM_BIN1(0)
        self.PWM_BIN2(0)

    def setPWM(self, Left, Right):
        self.PWM_LEFT = Left
        self.PWM_RIGHT = Right

    def getPWM(self):
        pass

    def stopPWM(self):
        self.PWM_AIN1.stop()
        self.PWM_AIN2.stop()
        self.PWM_BIN1.stop()
        self.PWM_BIN2.stop()