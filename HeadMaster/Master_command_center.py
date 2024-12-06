import socket
import time

# Socket-Setup
HOST = '0.0.0.0'  # Alle Schnittstellen
PORT = 12345
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((HOST, PORT))
sock.listen(1)

print("Warte auf Verbindung...")
conn, addr = sock.accept()
print(f"Verbunden mit {addr}")

try:
    while True:
        # Encoder-Daten vom Raspberry Pi empfangen
        data = conn.recv(1024).decode('utf-8')
        if data:
            left_ticks, right_ticks = map(int, data.split(","))
            print(f"Encoder: {left_ticks}, {right_ticks}")
        
        # Steuerbefehle senden (z. B. Geschwindigkeit)
        left_speed = 50  # Beispielwert
        right_speed = 50  # Beispielwert
        conn.send(f"{left_speed},{right_speed}\n".encode('utf-8'))
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Beendet")
finally:
    conn.close()
    sock.close()
