import RPi.GPIO as GPIO
import time
import threading
from simple_pid import PID  # Falls nicht installiert: pip install simple-pid

# GPIO Setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Motor Pins
AIN1 = 17
AIN2 = 18
BIN1 = 22
BIN2 = 23

# Encoder Pins
E1A = 20
E1B = 21
E2A = 26
E2B = 27

# Globale Variablen
class MotorControl:
    def __init__(self):
        self.p1 = None
        self.p2 = None
        self.p3 = None
        self.p4 = None
        self.spin_count1 = 0
        self.spin_count2 = 0
        self.target_rpm = 0
        self.current_rpm1 = 0
        self.current_rpm2 = 0
        self.running = True
        self.motor_power1 = 0
        self.motor_power2 = 0
        
        # PID-Regler für beide Motoren
        self.pid1 = PID(Kp=0.5, Ki=0.6, Kd=0.1, setpoint=0)
        self.pid2 = PID(Kp=0.5, Ki=0.6, Kd=0.1, setpoint=0)
        
        # Grenzen für PID-Ausgang
        self.pid1.output_limits = (0, 100)
        self.pid2.output_limits = (0, 100)

motor = MotorControl()

def setup_gpio():
    # Motor Pins Setup
    GPIO.setup(AIN1, GPIO.OUT)
    GPIO.setup(AIN2, GPIO.OUT)
    GPIO.setup(BIN1, GPIO.OUT)
    GPIO.setup(BIN2, GPIO.OUT)
    
    # PWM Objekte erstellen
    motor.p1 = GPIO.PWM(AIN1, 50)
    motor.p2 = GPIO.PWM(AIN2, 50)
    motor.p3 = GPIO.PWM(BIN1, 50)
    motor.p4 = GPIO.PWM(BIN2, 50)
    
    # PWM starten
    motor.p1.start(0)
    motor.p2.start(0)
    motor.p3.start(0)
    motor.p4.start(0)
    
    # Encoder Pins
    GPIO.setup(E1A, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(E1B, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(E2A, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(E2B, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def encoder1_callback(channel):
    if GPIO.input(E1A):
        if not GPIO.input(E1B):
            motor.spin_count1 += 1
        elif GPIO.input(E1B):
            motor.spin_count1 -= 1

def encoder2_callback(channel):
    if GPIO.input(E2A):
        if not GPIO.input(E2B):
            motor.spin_count2 += 1
        elif GPIO.input(E2B):
            motor.spin_count2 -= 1

def calculate_speed():
    last_count1 = 0
    last_count2 = 0
    last_time = time.time()
    
    while motor.running:
        current_time = time.time()
        time_diff = current_time - last_time
        
        if time_diff >= 0.1:  # Alle 100ms aktualisieren
            # Motor 1 RPM
            count_diff1 = motor.spin_count1 - last_count1
            motor.current_rpm1 = abs((count_diff1 / 20) * (60 / time_diff))  # 20 Impulse pro Umdrehung
            
            # Motor 2 RPM
            count_diff2 = motor.spin_count2 - last_count2
            motor.current_rpm2 = abs((count_diff2 / 20) * (60 / time_diff))
            
            last_count1 = motor.spin_count1
            last_count2 = motor.spin_count2
            last_time = current_time

def pid_control():
    while motor.running:
        # PID-Regelung für beide Motoren
        motor.pid1.setpoint = motor.target_rpm
        motor.pid2.setpoint = motor.target_rpm
        
        motor.motor_power1 = motor.pid1(motor.current_rpm1)
        motor.motor_power2 = motor.pid2(motor.current_rpm2)
        
        set_motor_speed(motor.motor_power1, motor.motor_power2)
        time.sleep(0.05)

def set_motor_speed(power1, power2):
    # Vorwärtsrichtung
    motor.p1.ChangeDutyCycle(0)
    motor.p2.ChangeDutyCycle(power1)
    motor.p3.ChangeDutyCycle(0)
    motor.p4.ChangeDutyCycle(power2)

def stop_motors():
    motor.p1.ChangeDutyCycle(0)
    motor.p2.ChangeDutyCycle(0)
    motor.p3.ChangeDutyCycle(0)
    motor.p4.ChangeDutyCycle(0)

def display_info():
    while motor.running:
        print(f"\rZiel: {motor.target_rpm:.1f} RPM | "
              f"Motor1: {motor.current_rpm1:.1f} RPM ({motor.motor_power1:.1f}%) | "
              f"Motor2: {motor.current_rpm2:.1f} RPM ({motor.motor_power2:.1f}%)", end="")
        time.sleep(0.1)

def main():
    try:
        # Setup
        setup_gpio()
        GPIO.add_event_detect(E1A, GPIO.RISING, callback=encoder1_callback)
        GPIO.add_event_detect(E2A, GPIO.RISING, callback=encoder2_callback)
        
        # Threads starten
        speed_thread = threading.Thread(target=calculate_speed)
        pid_thread = threading.Thread(target=pid_control)
        display_thread = threading.Thread(target=display_info)
        
        speed_thread.start()
        pid_thread.start()
        display_thread.start()
        
        print("Motorsteuerung bereit. Geben Sie die gewünschte Geschwindigkeit in RPM ein (0-200).")
        print("Zum Beenden 'q' eingeben.")
        
        while True:
            user_input = input()
            if user_input.lower() == 'q':
                break
            try:
                rpm = float(user_input)
                if 0 <= rpm <= 200:
                    motor.target_rpm = rpm
                else:
                    print("Bitte einen Wert zwischen 0 und 200 RPM eingeben.")
            except ValueError:
                print("Ungültige Eingabe. Bitte eine Zahl eingeben.")
        
    except KeyboardInterrupt:
        print("\nProgramm wird beendet...")
    
    finally:
        motor.running = False
        stop_motors()
        GPIO.cleanup()
        print("\nProgramm beendet.")

if __name__ == "__main__":
    main()