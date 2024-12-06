import socket
import time

# Socket-Setup
HOST = '0.0.0.0'  # Hört auf alle Schnittstellen
PORT = 12345
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((HOST, PORT))
sock.listen(1)

print("Warte auf Verbindung...")
conn, addr = sock.accept()
print(f"Verbunden mit {addr}")

sock.settimeout(1)  # Timeout nach 5 Sekunden

try:
    # Handshake: Warte auf Nachricht vom Raspberry Pi
    message = conn.recv(1024).decode('utf-8').strip()
    print("Handshake erhalten:", message)
    if message == "HELLO_PC":
        conn.send("HELLO_PI\n".encode('utf-8'))
        print("Antwort gesendet: HELLO_PI")
    else:
        print("Unerwartete Handshake-Nachricht:", message)
    time.sleep(1)
    # Hauptschleife (Dummy-Daten empfangen und antworten)
    while True:
        print("Warte auf Daten...")
        try:
            # Versuche, Daten zu empfangen
            data = conn.recv(1024).decode('utf-8').strip()
            if not data:
                print("Keine Daten empfangen, weiter mit der nächsten Iteration...")
                continue  # Rücksprung zum Anfang der Schleife, wenn keine Daten empfangen wurden

            print("Daten empfangen:", data)

            # Daten weiterverarbeiten
            left_ticks, right_ticks = data.split(",")
            print(f"Encoder: {left_ticks}, {right_ticks}")

            # Steuerbefehle senden (z. B. Geschwindigkeit)
            left_speed = 50  # Beispielwert
            right_speed = 50  # Beispielwert
            conn.send(f"{left_speed},{right_speed}\n".encode('utf-8'))

        except socket.timeout:
            # Timeout ausgelöst, keine Daten empfangen
            print("Timeout: Keine Daten empfangen, versuche es erneut.")
            continue  # Weiter mit der nächsten Iteration

except KeyboardInterrupt:
    print("Beendet durch Benutzer")
finally:
    conn.close()
    sock.close()
