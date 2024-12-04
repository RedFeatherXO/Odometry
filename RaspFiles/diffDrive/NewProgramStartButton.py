import RPi.GPIO as GPIO
import time
import subprocess
import os
import signal

# Pin-Nummer für den Button
BUTTON_PIN = 16
READY_LED_PIN = 25
STARTED_LED_PIN = 12

# Name des Main-Programms, das du nur einmal laufen lassen willst
MAIN_PROGRAM_PATH = "/home/pi/Documents/diffDrive/test.py"

# GPIO-Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(READY_LED_PIN, GPIO.OUT)
GPIO.setup(STARTED_LED_PIN, GPIO.OUT)

GPIO.output(READY_LED_PIN,GPIO.LOW)
GPIO.output(STARTED_LED_PIN,GPIO.LOW)

def is_program_running():
    """Prüft, ob das Main-Programm bereits läuft."""
    try:
        # Verwende pgrep, um nach dem Main-Programm zu suchen
        result = subprocess.check_output(["pgrep", "-f", MAIN_PROGRAM_PATH])
        # Wenn pgrep eine PID findet, läuft das Programm bereits
        return bool(result.strip())
    except subprocess.CalledProcessError:
        # pgrep hat nichts gefunden, das Programm läuft also nicht
        return False

def start_program():
    """Startet das Main-Programm in einem Terminal, wenn es nicht läuft."""
    if not is_program_running():
        print("Programm wird gestartet...")
        GPIO.output(STARTED_LED_PIN,GPIO.HIGH)
        # Öffne das Programm in einem neuen Terminal
        subprocess.Popen(["lxterminal", "-e", f"python3 {MAIN_PROGRAM_PATH}"])
    else:
        print("Programm läuft bereits.")

print("Button drücken zum starten")
GPIO.output(READY_LED_PIN,GPIO.HIGH)
try:
    while True:
        # Prüfen, ob der Button gedrückt ist
        print(f"Button state wird gelesen: {GPIO.input(BUTTON_PIN)}")
        if GPIO.input(BUTTON_PIN) == GPIO.HIGH:
            print("Button gedrückt.")
            start_program()
            # Warten, bis der Button losgelassen wird, um Mehrfachstarts zu verhindern
            while GPIO.input(BUTTON_PIN) == GPIO.HIGH:
                time.sleep(0.4)
        time.sleep(0.4)  # Kurze Verzögerung, um CPU-Auslastung zu reduzieren

except KeyboardInterrupt:
    print("Programm wird beendet.")
finally:
    GPIO.cleanup()
