import RPi.GPIO as GPIO
import socket
import time

# GPIO-Setup
AIN1 = 17
AIN2 = 18
PWM_FREQ = 50

GPIO.setmode(GPIO.BCM)
GPIO.setup(AIN1, GPIO.OUT)
GPIO.setup(AIN2, GPIO.OUT)

pwm1 = GPIO.PWM(AIN1, PWM_FREQ)
pwm2 = GPIO.PWM(AIN2, PWM_FREQ)
pwm1.start(0)
pwm2.start(0)

# Socket-Setup
HOST = '192.168.178.20'  # IP-Adresse des PCs
PORT = 12345
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

print("Versuche Verbindung mit dem PC...")
sock.connect((HOST, PORT))
print("Verbindung hergestellt!")

sock.settimeout(1)  # Timeout nach 5 Sekunden

try:
    # Handshake: Sende Testnachricht an PC
    sock.send("HELLO_PC\n".encode('utf-8'))
    print("Handshake gesendet: HELLO_PC")

    # Warte auf Antwort vom PC
    response = sock.recv(1024).decode('utf-8').strip()
    if response == "HELLO_PI":
        print("Handshake erfolgreich: Antwort vom PC erhalten ->", response)
    else:
        print("Unerwartete Antwort vom PC:", response)

    time.sleep(1)
    # Hauptschleife (Dummy-Daten senden)
    while True:
        try:
            # Daten vom PC empfangen
            data = sock.recv(1024).decode('utf-8')
            if data:
                left_speed, right_speed = map(int, data.split(","))
                
                # PWM-Signale setzen
                pwm1.ChangeDutyCycle(left_speed)
                pwm2.ChangeDutyCycle(right_speed)
            
            # Encoder-Werte simulieren (z. B. Zufallswerte oder GPIO-Eingaben)
            left_ticks = 10  # Hier echte Encoder-Daten verwenden
            right_ticks = 12  # Hier echte Encoder-Daten verwenden
            
            # Daten an PC senden
            sock.send(f"{left_ticks},{right_ticks}\n".encode('utf-8'))
            time.sleep(0.1)
        except socket.timeout:
            # Timeout ausgelöst, keine Daten empfangen
            sock.send(f"{10},{12}\n".encode('utf-8'))
            print("Timeout: Keine Daten empfangen, versuche es erneut.")
            continue  # Weiter mit der nächsten Iteration

except KeyboardInterrupt:
    print("Beendet durch Benutzer")
finally:
    pwm1.stop()
    pwm2.stop()
    sock.close()
    GPIO.cleanup()
