import RPi.GPIO as GPIO
import time
import threading
import numpy as np
from simple_pid import PID
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque

# GPIO Setup wie zuvor
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Motor & Encoder Pins
AIN1, AIN2 = 17, 18
BIN1, BIN2 = 22, 23
E1A, E1B = 20, 21
E2A, E2B = 26, 27

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
        self.tuning_mode = False
        
        # Speicher für Plotting
        self.time_points = deque(maxlen=100)
        self.rpm1_points = deque(maxlen=100)
        self.rpm2_points = deque(maxlen=100)
        self.target_points = deque(maxlen=100)
        
        # PID-Regler (werden später initialisiert)
        self.pid1 = None
        self.pid2 = None
        
        # Ziegler-Nichols Parameter
        self.Ku = 0  # Kritische Verstärkung
        self.Tu = 0  # Kritische Periodendauer

motor = MotorControl()

def setup_gpio():
    # Motor Pins Setup
    for pin in [AIN1, AIN2, BIN1, BIN2]:
        GPIO.setup(pin, GPIO.OUT)
    
    # PWM Initialisierung
    motor.p1 = GPIO.PWM(AIN1, 50)
    motor.p2 = GPIO.PWM(AIN2, 50)
    motor.p3 = GPIO.PWM(BIN1, 50)
    motor.p4 = GPIO.PWM(BIN2, 50)
    
    for p in [motor.p1, motor.p2, motor.p3, motor.p4]:
        p.start(0)
    
    # Encoder Setup
    for pin in [E1A, E1B, E2A, E2B]:
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def ziegler_nichols_tuning():
    print("\nStarte Ziegler-Nichols Tuning...")
    print("1. Erhöhe Kp bis zur Oszillation")
    print("2. Messe Ku (kritische Verstärkung) und Tu (Schwingungsperiode)")
    
    # Initialer P-Regler
    motor.pid1 = PID(Kp=0.1, Ki=0, Kd=0, setpoint=100)
    motor.pid1.output_limits = (0, 100)
    
    try:
        while True:
            current_kp = input("Geben Sie Kp ein (oder 'f' wenn fertig): ")
            if current_kp.lower() == 'f':
                break
            try:
                motor.pid1.Kp = float(current_kp)
                time.sleep(2)  # Zeit zum Beobachten der Reaktion
            except ValueError:
                print("Bitte eine gültige Zahl eingeben.")
        
        # Ku und Tu abfragen
        while True:
            try:
                motor.Ku = float(input("Geben Sie Ku (kritische Verstärkung) ein: "))
                motor.Tu = float(input("Geben Sie Tu (Schwingungsperiode in Sekunden) ein: "))
                break
            except ValueError:
                print("Bitte eine gültige Zahl eingeben.")
        
        # Ziegler-Nichols Formeln
        Kp = 0.6 * motor.Ku
        Ti = 0.5 * motor.Tu
        Td = 0.125 * motor.Tu
        
        Ki = Kp / Ti
        Kd = Kp * Td
        
        print(f"\nBerechnete PID-Parameter:")
        print(f"Kp = {Kp:.3f}")
        print(f"Ki = {Ki:.3f}")
        print(f"Kd = {Kd:.3f}")
        
        # Neue PID-Regler mit berechneten Parametern
        motor.pid1 = PID(Kp=Kp, Ki=Ki, Kd=Kd, setpoint=motor.target_rpm)
        motor.pid2 = PID(Kp=Kp, Ki=Ki, Kd=Kd, setpoint=motor.target_rpm)
        motor.pid1.output_limits = (0, 100)
        motor.pid2.output_limits = (0, 100)
        
    except ValueError:
        print("Ungültige Eingabe!")


def manual_tuning():
    print("\nManuelles PID-Tuning")
    try:
        kp = float(input("Geben Sie Kp ein: "))
        ki = float(input("Geben Sie Ki ein: "))
        kd = float(input("Geben Sie Kd ein: "))
        
        motor.pid1 = PID(Kp=kp, Ki=ki, Kd=kd, setpoint=motor.target_rpm)
        motor.pid2 = PID(Kp=kp, Ki=ki, Kd=kd, setpoint=motor.target_rpm)
        motor.pid1.output_limits = (0, 100)
        motor.pid2.output_limits = (0, 100)
        
    except ValueError:
        print("Ungültige Eingabe!")

def init_plot():
    plt.ion()
    fig, ax = plt.subplots(figsize=(10, 6))
    line_target, = ax.plot([], [], 'r-', label='Ziel-RPM')
    line_rpm1, = ax.plot([], [], 'b-', label='Motor 1 RPM')
    line_rpm2, = ax.plot([], [], 'g-', label='Motor 2 RPM')
    
    ax.set_ylim(0, 250)
    ax.set_xlabel('Zeit (s)')
    ax.set_ylabel('RPM')
    ax.set_title('Motor-Geschwindigkeit')
    ax.grid(True)
    ax.legend()
    
    return fig, ax, line_target, line_rpm1, line_rpm2

def update_plot():
    fig, ax, line_target, line_rpm1, line_rpm2 = init_plot()
    
    while motor.running:
        current_time = time.time()
        motor.time_points.append(current_time - min(motor.time_points, default=current_time))
        motor.rpm1_points.append(motor.current_rpm1)
        motor.rpm2_points.append(motor.current_rpm2)
        motor.target_points.append(motor.target_rpm)
        
        line_target.set_data(list(motor.time_points), list(motor.target_points))
        line_rpm1.set_data(list(motor.time_points), list(motor.rpm1_points))
        line_rpm2.set_data(list(motor.time_points), list(motor.rpm2_points))
        
        ax.relim()
        ax.autoscale_view()
        fig.canvas.draw()
        fig.canvas.flush_events()
        
        time.sleep(0.1)

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

def main():
    try:
        setup_gpio()
        GPIO.add_event_detect(E1A, GPIO.RISING, callback=encoder1_callback)
        GPIO.add_event_detect(E2A, GPIO.RISING, callback=encoder2_callback)
        
        print("\nPID-Tuning-Methode wählen:")
        print("1: Ziegler-Nichols-Methode")
        print("2: Manuelles Tuning")
        choice = input("Wählen Sie (1/2): ")
        
        if choice == '1':
            ziegler_nichols_tuning()
        else:
            manual_tuning()
        
        # Threads starten
        threads = [
            threading.Thread(target=calculate_speed),
            threading.Thread(target=pid_control),
            threading.Thread(target=update_plot)
        ]
        
        for thread in threads:
            thread.start()
        
        print("\nSteuerung bereit. Befehle:")
        print("- Zahl: Neue Ziel-RPM (0-200)")
        print("- 't': PID-Parameter anpassen")
        print("- 'q': Beenden")
        
        while True:
            cmd = input()
            if cmd.lower() == 'q':
                break
            elif cmd.lower() == 't':
                manual_tuning()
            else:
                try:
                    rpm = float(cmd)
                    if 0 <= rpm <= 200:
                        motor.target_rpm = rpm
                        motor.pid1.setpoint = rpm
                        motor.pid2.setpoint = rpm
                    else:
                        print("RPM muss zwischen 0 und 200 liegen")
                except ValueError:
                    print("Ungültige Eingabe")
    
    except KeyboardInterrupt:
        print("\nProgramm wird beendet...")
    
    finally:
        motor.running = False
        stop_motors()
        GPIO.cleanup()
        plt.close('all')
        print("\nProgramm beendet.")

if __name__ == "__main__":
    main()