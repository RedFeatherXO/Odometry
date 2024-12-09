import socket
import time
import select
import threading

class SocketServer:
    def __init__(self, host='0.0.0.0', port=12345):
        """
        Initialisiert den Socket-Server mit Host und Port.
        
        :param host: Hostname oder IP-Adresse (Standard: '0.0.0.0')
        :param port: Port-Nummer (Standard: 12345)
        """
        self.HOST = host
        self.PORT = port
        self.sock = None
        self.connection = None
        self.address = None
        self.is_running = False
        self.connection_thread = None
        self.AllTicksRight = 0
        self.AllTicksLeft = 0

    def start_server(self):
        """
        Startet den Server und wartet auf Verbindungen.
        """
        try:
            # Socket-Setup
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.bind((self.HOST, self.PORT))
            self.sock.listen(1)
            
            # Socket in den nicht-blockierenden Modus setzen
            self.sock.setblocking(False)
            
            print(f"Server gestartet auf {self.HOST}:{self.PORT}")
            self.is_running = True
            
            # Thread für Verbindungsannahme starten
            self.connection_thread = threading.Thread(target=self._accept_connections)
            self.connection_thread.start()
            
        except Exception as e:
            print(f"Fehler beim Starten des Servers: {e}")
            self.is_running = False

    def _accept_connections(self):
        """
        Interner Thread zum Annehmen von Verbindungen.
        """
        while self.is_running:
            try:
                # select() verwendet, um auf eingehende Verbindungen zu warten
                readable, _, _ = select.select([self.sock], [], [], 1.0)
                
                if readable:
                    self.connection, self.address = self.sock.accept()
                    print(f"Verbunden mit {self.address}")
                    
                    # Verbindungs-Socket nicht-blockierend machen
                    self.connection.setblocking(False)
                    
                    # Handshake durchführen
                    self._perform_handshake()
                    
                    # Hauptkommunikationsschleife starten
                    self._communication_loop()
            
            except Exception as e:
                print(f"Verbindungsfehler: {e}")
                break
            
            time.sleep(0.5)

    def _perform_handshake(self):
        """
        Führt den Handshake mit dem Client durch.
        """
        try:
            message = self.connection.recv(1024).decode('utf-8').strip()
            print("Handshake erhalten:", message)
            
            if message == "HELLO_PC":
                self.connection.send("HELLO_PI\n".encode('utf-8'))
                print("Antwort gesendet: HELLO_PI")
            else:
                print("Unerwartete Handshake-Nachricht:", message)
        
        except BlockingIOError:
            print("Kein Handshake-Daten empfangen")

    def _communication_loop(self):
        """
        Hauptkommunikationsschleife für empfangene Nachrichten.
        """
        while self.is_running and self.connection:
            try:
                # select() verwenden, um zu prüfen, ob Daten verfügbar sind
                ready = select.select([self.connection], [], [], 1.0)
                
                if ready[0]:
                    data = self.connection.recv(1024).decode('utf-8').strip()
                    
                    if not data:
                        print("Verbindung geschlossen")
                        break
                    
                    # Daten verarbeiten
                    self._process_data(data)
                
                time.sleep(0.1)  # Kleine Pause zur Reduzierung der CPU-Auslastung
            
            except (ConnectionResetError, BrokenPipeError):
                print("Verbindung unterbrochen")
                break
            
            except BlockingIOError:
                # Keine Daten verfügbar, weiter
                pass

    def _process_data(self, data):
        """
        Verarbeitet empfangene Daten. 
        Kann in Unterklassen überschrieben werden für spezifische Anwendungsfälle.
        
        :param data: Empfangene Daten als String
        """
        try:
            # Beispiel für Datenverarbeitung
            left_ticks, right_ticks = data.split(",")
            self.AllTicksRight += right_ticks
            self.AllTicksLeft += left_ticks
            print(f"Encoder: {left_ticks}, {right_ticks}")
            
            # Optional: Steuerbefehle senden
            # left_speed = 50
            # right_speed = 50
            # self.connection.send(f"{left_speed},{right_speed}\n".encode('utf-8'))
        
        except ValueError as ve:
            print(f"Fehler beim Verarbeiten der Daten: {ve}")

    def GetAllTicks(self):
        return self.AllTicksRight, self.AllTicksLeft

    def stop_server(self):
        """
        Stoppt den Server und schließt alle Verbindungen.
        """
        self.is_running = False
        
        if self.connection:
            self.connection.close()
        
        if self.sock:
            self.sock.close()
        
        if self.connection_thread:
            self.connection_thread.join()
        
        print("Server gestoppt")

# Beispielhafte Verwendung
if __name__ == "__main__":
    try:
        server = SocketServer()
        server.start_server()
        
        # Halten Sie das Hauptprogramm am Laufen
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("Beendet durch Benutzer")
    
    finally:
        server.stop_server()