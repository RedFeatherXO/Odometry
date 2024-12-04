import RPi.GPIO as GPIO
import time
import subprocess  # Zum Starten des Programms

# Pin-Nummer festlegen (in diesem Beispiel GPIO 17)
BUTTON_PIN = 16

# GPIO-Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def start_program():
    # Hier den Pfad zu deinem Python-Programm angeben
    subprocess.Popen(["python3", "/home/pi/Documents/diffDrive/test.py"])

print("Button drücken zum starten")

try:
    while True:
        # Prüfen, ob der Button gedrückt ist
        print(f"GPIO: {GPIO.input(BUTTON_PIN)}")
        if GPIO.input(BUTTON_PIN) == GPIO.HIGH:
            print("Button gedrückt, Programm wird gestartet...")
            start_program()
            # Warten, bis der Button losgelassen wird, um Mehrfachstarts zu verhindern
            while GPIO.input(BUTTON_PIN) == GPIO.HIGH:
                time.sleep(0.1)
        time.sleep(0.1)  # Kurze Verzögerung, um CPU-Auslastung zu reduzieren

except KeyboardInterrupt:
    print("Programm wird beendet.")
finally:
    GPIO.cleanup()
