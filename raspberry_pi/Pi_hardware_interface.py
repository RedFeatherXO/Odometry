import socket
import time
import select
import RPi.GPIO as GPIO
from encoder_Reader import EncoderReader

encoderReader = EncoderReader(20,21,26,27)

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

# Setze Socket in nicht-blockierenden Modus
sock.setblocking(False)

print("Versuche Verbindung mit dem PC...")
try:
    sock.connect((HOST, PORT))
except BlockingIOError:
    # Dieser Fehler ist normal beim nicht-blockierenden connect
    pass

print("Verbindung hergestellt!")

try:
    # Handshake: Sende Testnachricht an PC
    sock.send("HELLO_PC\n".encode('utf-8'))
    print("Handshake gesendet: HELLO_PC")

    # Warte auf Antwort vom PC mit Timeout
    start_time = time.time()
    response = ""
    while not response:
        try:
            response = sock.recv(1024).decode('utf-8').strip()
        except BlockingIOError:
            # Keine Daten verfügbar
            if time.time() - start_time > 5:  # 5 Sekunden Timeout
                print("Timeout beim Warten auf Handshake-Antwort")
                break
            time.sleep(0.1)

    if response == "HELLO_PI":
        print("Handshake erfolgreich: Antwort vom PC erhalten ->", response)
    else:
        print("Unerwartete Antwort vom PC:", response)

    # Hauptschleife
    while True:
        try:
            # Versuche, Daten zu empfangen
            readable, _, _ = select.select([sock], [], [], 0.1)
            
            if readable:
                data = sock.recv(1024).decode('utf-8').strip()
                print("Empfangene Daten:", data)  # Debug-Ausgabe
                
                if data:
                    left_speed, right_speed = map(int, data.split(","))
                    
                    # PWM-Signale setzen
                    pwm1.ChangeDutyCycle(left_speed)
                    pwm2.ChangeDutyCycle(right_speed)
            
            # Encoder-Werte abrufen
            left_ticks, right_ticks = encoderReader.GetValues() 
            
            # Daten an PC senden
            try:
                sock.send(f"{left_ticks},{right_ticks}\n".encode('utf-8'))
            except (BrokenPipeError, ConnectionResetError):
                print("Verbindung zum PC unterbrochen")
                break
            
            time.sleep(0.1)

        except Exception as e:
            print(f"Fehler in Hauptschleife: {e}")
            time.sleep(0.1)

except KeyboardInterrupt:
    print("Beendet durch Benutzer")
finally:
    pwm1.stop()
    pwm2.stop()
    sock.close()
    GPIO.cleanup()