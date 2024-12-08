import socket
import time
import select
import errno
import RPi.GPIO as GPIO
from encoder_Reader import EncoderReader
from Motor_Driver import MotorDriver
from GPIO_Manager import GPIOManager

GPIO.cleanup()  # Räumt alle vorherigen GPIO-Einstellungen auf
gpioManager = GPIOManager()
encoderReader = EncoderReader(20,21,26,27)
motorDriver  = MotorDriver(17,18,22,23)

# Socket-Setup
HOST = '192.168.178.20'  # IP-Adresse des PCs
PORT = 12345
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Setze Socket in nicht-blockierenden Modus
sock.setblocking(False)

print("Versuche Verbindung mit dem PC...")

# Verbindungsaufbau mit Timeout-Behandlung
try:
    sock.connect((HOST, PORT))
except (socket.error, BlockingIOError) as e:
    # Prüfe, ob Verbindung in Arbeit ist
    if e.errno != errno.EINPROGRESS:
        print(f"Verbindungsfehler: {e}")
        sock.close()
        exit(1)

# Warte auf Verbindungsaufbau
start_time = time.time()
while time.time() - start_time < 10:  # 10 Sekunden Timeout
    try:
        # Prüfe Verbindungsstatus
        sock.send(b'')  # Versuche, Daten zu senden
        break  # Erfolgreich verbunden
    except BlockingIOError:
        # Verbindung noch nicht bereit
        try:
            # Überprüfe Fehler mit select
            _, writable, _ = select.select([], [sock], [], 1.0)
            if writable:
                break  # Verbindung hergestellt
        except select.error:
            pass
        time.sleep(0.1)
else:
    print("Verbindungsaufbau fehlgeschlagen")
    sock.close()
    exit(1)

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
        motorDriver.DriveForward()
        try:
            # Versuche, Daten zu empfangen
            # readable, _, _ = select.select([sock], [], [], 0.1)
            
            # if readable:
            #     try:
            #         data = sock.recv(1024).decode('utf-8').strip()
            #         print("Empfangene Daten:", data)  # Debug-Ausgabe
                    
            #         if data:
            #             left_speed, right_speed = map(int, data.split(","))
                        
            #             # PWM-Signale setzen
            #             pwm1.ChangeDutyCycle(left_speed)
            #             pwm2.ChangeDutyCycle(right_speed)
            #     except BlockingIOError:
            #         pass
            
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
    motorDriver.DriveStop()
    motorDriver.stopPWM()
    sock.close()
    GPIO.cleanup()