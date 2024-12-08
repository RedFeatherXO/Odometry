import socket
import time
import select  # Wichtige Ergänzung für nicht-blockierende E/A

# Socket-Setup
HOST = '0.0.0.0'
PORT = 12345
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((HOST, PORT))
sock.listen(1)

# Socket in den nicht-blockierenden Modus setzen
sock.setblocking(False)

print("Warte auf Verbindung...")

try:
    while True:
        # select() verwendet, um auf eingehende Verbindungen zu warten
        readable, _, _ = select.select([sock], [], [], 1.0)
        
        if readable:
            conn, addr = sock.accept()
            print(f"Verbunden mit {addr}")
            
            # Verbindungs-Socket auch nicht-blockierend machen
            conn.setblocking(False)
            
            # Handshake
            try:
                message = conn.recv(1024).decode('utf-8').strip()
                print("Handshake erhalten:", message)
                if message == "HELLO_PC":
                    conn.send("HELLO_PI\n".encode('utf-8'))
                    print("Antwort gesendet: HELLO_PI")
                else:
                    print("Unerwartete Handshake-Nachricht:", message)
            except BlockingIOError:
                print("Kein Handshake-Daten empfangen")
            
            # Hauptkommunikationsschleife
            while True:
                try:
                    # select() verwenden, um zu prüfen, ob Daten verfügbar sind
                    ready = select.select([conn], [], [], 1.0)
                    #print(f"ready: {ready}")
                    if ready[0]:
                        #print("conn.recv")
                        data = conn.recv(1024).decode('utf-8').strip()
                        if not data:
                            print("Verbindung geschlossen")
                            break
                        
                        #print("Daten empfangen:", data)
                        
                        try:
                            # Daten weiterverarbeiten
                            left_ticks, right_ticks = data.split(",")
                            print(f"Encoder: {left_ticks}, {right_ticks}")
                            
                            # Steuerbefehle senden
                            # left_speed = 50
                            # right_speed = 50
                            # conn.send(f"{left_speed},{right_speed}\n".encode('utf-8'))
                        except ValueError as ve:
                            #print(f"Fehler beim Verarbeiten der Daten: {ve}")
                            #print(f"Empfangene Daten: {data}")
                            continue
                    
                    time.sleep(0.1)  # Kleine Pause, um CPU-Auslastung zu reduzieren
                
                except (ConnectionResetError, BrokenPipeError):
                    print("Verbindung unterbrochen")
                    break
                except BlockingIOError:
                    # Keine Daten verfügbar, weiter
                    pass
        
        time.sleep(0.5)  # Kleine Pause in der äußeren Schleife

except KeyboardInterrupt:
    print("Beendet durch Benutzer")
finally:
    sock.close()