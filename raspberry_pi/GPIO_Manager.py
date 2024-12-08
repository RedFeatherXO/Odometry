# gpio_manager.py
import RPi.GPIO as GPIO

class GPIOManager:
    def __init__(self):
        # Einmalige GPIO-Initialisierung
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

    def reset(self):
        # Optional: Alle GPIO-Kanäle zurücksetzen
        GPIO.cleanup()