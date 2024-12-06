import RPi.GPIO as GPIO
import socket
import time

# GPIO-Setup (falls benötigt)
GPIO.setmode(GPIO.BCM)

# Socket-Setup
HOST = '192.168.0.104'  # IP-Adresse des PCs
PORT = 12345
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

print("Versuche Verbindung mit dem PC...")
sock.connect((HOST, PORT))
print("Verbindung hergestellt!")

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

    # Hauptschleife (Dummy-Daten senden)
    while True:
        data_to_send = "DATA_FROM_PI,42,84\n"
        sock.send(data_to_send.encode('utf-8'))
        print("Gesendet:", data_to_send.strip())
        
        # Warte auf Antwort (zum Test)
        response = sock.recv(1024).decode('utf-8').strip()
        print("Antwort vom PC:", response)

        time.sleep(1)

except KeyboardInterrupt:
    print("Beendet durch Benutzer")
finally:
    sock.close()
    GPIO.cleanup()
