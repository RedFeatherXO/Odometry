import RPi.GPIO as GPIO
import time

class EncoderReader:
    def __init__(self,E1A_Pin,E1B_Pin,E2A_Pin,E2B_Pin):
        self.E1A = E1A_Pin
        self.E1B = E1B_Pin
        self.E2A = E2A_Pin
        self.E2B = E2B_Pin
        self.spin_count1 = 0
        self.spin_count2 = 0
        self.setup_gpio()

    def setup_gpio(self):
        GPIO.setup(self.E1A,GPIO.IN,pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.E1B,GPIO.IN,pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.E2A,GPIO.IN,pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.E2B,GPIO.IN,pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(self.E1A,GPIO.RISING,callback=self.myCallBack1)
        GPIO.add_event_detect(self.E2A,GPIO.RISING,callback=self.myCallBack2)
    
    def GetValues(self):
        return self.spin_count1,self.spin_count2
              
    def myCallBack1(self,channel):
        if not GPIO.input(self.E1B):
            self.spin_count1 += 1
        elif GPIO.input(self.E1B):
            self.spin_count1 -= 1

    def myCallBack2(self,channel):
        if not GPIO.input(self.E2B):
            self.spin_count2 += 1
        elif GPIO.input(self.E2B):
            self.spin_count2 -= 1









