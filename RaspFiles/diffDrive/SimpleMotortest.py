import RPi.GPIO as GPIO
import time

# GPIO Setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Motor Pins
AIN1 = 17
AIN2 = 18
BIN1 = 22
BIN2 = 23

def setup():
    # Setup der Motor-Pins
    pins = [AIN1, AIN2, BIN1, BIN2]
    for pin in pins:
        GPIO.setup(pin, GPIO.OUT)
        print(f"Pin {pin} als Ausgang konfiguriert")

def test_motors():
    try:
        # Motor 1
        pwm_a1 = GPIO.PWM(AIN1, 50)
        pwm_a2 = GPIO.PWM(AIN2, 50)
        # Motor 2
        pwm_b1 = GPIO.PWM(BIN1, 50)
        pwm_b2 = GPIO.PWM(BIN2, 50)

        # PWM starten
        for pwm in [pwm_a1, pwm_a2, pwm_b1, pwm_b2]:
            pwm.start(0)
            print("PWM gestartet")

        while True:
            print("\nMotortest-Menü:")
            print("1: Motor 1 vorwärts")
            print("2: Motor 2 vorwärts")
            print("3: Beide Motoren vorwärts")
            print("4: Stop")
            print("5: Test verschiedener Geschwindigkeiten")
            print("q: Beenden")
            
            choice = input("Wählen Sie eine Option: ")
            
            if choice == '1':
                print("Motor 1 vorwärts")
                pwm_a1.ChangeDutyCycle(0)
                pwm_a2.ChangeDutyCycle(50)
                pwm_b1.ChangeDutyCycle(0)
                pwm_b2.ChangeDutyCycle(0)
            
            elif choice == '2':
                print("Motor 2 vorwärts")
                pwm_a1.ChangeDutyCycle(0)
                pwm_a2.ChangeDutyCycle(0)
                pwm_b1.ChangeDutyCycle(0)
                pwm_b2.ChangeDutyCycle(50)
            
            elif choice == '3':
                print("Beide Motoren vorwärts")
                pwm_a1.ChangeDutyCycle(0)
                pwm_a2.ChangeDutyCycle(50)
                pwm_b1.ChangeDutyCycle(0)
                pwm_b2.ChangeDutyCycle(50)
            
            elif choice == '4':
                print("Stoppe Motoren")
                for pwm in [pwm_a1, pwm_a2, pwm_b1, pwm_b2]:
                    pwm.ChangeDutyCycle(0)
            
            elif choice == '5':
                print("Teste verschiedene Geschwindigkeiten")
                for speed in [20, 40, 60, 80, 100]:
                    print(f"\nGeschwindigkeit: {speed}%")
                    pwm_a1.ChangeDutyCycle(0)
                    pwm_a2.ChangeDutyCycle(speed)
                    pwm_b1.ChangeDutyCycle(0)
                    pwm_b2.ChangeDutyCycle(speed)
                    time.sleep(2)
                print("Test beendet")
                for pwm in [pwm_a1, pwm_a2, pwm_b1, pwm_b2]:
                    pwm.ChangeDutyCycle(0)
            
            elif choice.lower() == 'q':
                print("Beende Programm")
                break
            
            else:
                print("Ungültige Eingabe")

    except KeyboardInterrupt:
        print("\nProgramm wird beendet...")
    
    finally:
        # Cleanup
        GPIO.cleanup()
        print("GPIO cleanup durchgeführt")

if __name__ == "__main__":
    print("Starte Motortest...")
    setup()
    test_motors()