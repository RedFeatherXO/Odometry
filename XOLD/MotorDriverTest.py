import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
AIN1 = 17
AIN2 = 18
BIN1 = 22
BIN2 = 23

GPIO.setwarnings(False)
GPIO.setup(AIN1,GPIO.OUT)
p1 = GPIO.PWM(AIN1, 50)
p1.start(0)

GPIO.setup(AIN2, GPIO.OUT)
p2 = GPIO.PWM(AIN2,50)
p2.start(0)

GPIO.setup(BIN1,GPIO.OUT)
p3 = GPIO.PWM(BIN1,50)
p3.start(0)

GPIO.setup(BIN2,GPIO.OUT)
p4 = GPIO.PWM(BIN2,50)
p4.start(0)

def forward(time_sleep):
    p1.start(0)
    p2.start(50)
    p3.start(0)
    p4.start(50)
    time.sleep(time_sleep)

def stop():
    p1.start(0)
    p2.start(0)
    p3.start(0)
    p4.start(0)

spin_count = 0
spin_count2 = 0
E1A = 20
E1B = 21
E2A = 27
E2B = 27
GPIO.setmode(GPIO.BCM)
GPIO.setup(E1B,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(E1A,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(E2B,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(E2A,GPIO.IN,pull_up_down=GPIO.PUD_UP)

def my_callback(channel):
    global spin_count
    if not GPIO.input(E1B):
        spin_count += 1
    elif GPIO.input(E1B):
        spin_count -= 1
    print(spin_count)

def my_callback2(channel):
    global spin_count2
    if not GPIO.input(E2B):
        spin_count2 += 1
    elif GPIO.input(E2B):
        spin_count2 -= 1
    print(spin_count2) 

GPIO.add_event_detect(E1A,GPIO.RISING,callback=my_callback)
GPIO.add_event_detect(E2A,GPIO.RISING,callback=my_callback2)

forward(5)
stop()











