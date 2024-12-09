import RPi.GPIO as GPIO
import time

class EncoderReader:
    def __init__(self,E1A_Pin,E1B_Pin,E2A_Pin,E2B_Pin):
        self.E1A = E1A_Pin #Motor 1
        self.E1B = E1B_Pin #Motor 1
        self.E2A = E2A_Pin #Motor 2
        self.E2B = E2B_Pin #Motor 2
        self.spin_count1 = 0 #Motor 1
        self.spin_count2 = 0 #Motor 2
        self.last_time1 = 0  # Letztes Ereignis für Encoder 1
        self.last_time2 = 0  # Letztes Ereignis für Encoder 2
        self.debounce_time = 0.002  # Entprellzeit in Sekunden
        self.setup_gpio()

    def setup_gpio(self):
        GPIO.setup(self.E1A,GPIO.IN,pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.E1B,GPIO.IN,pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.E2A,GPIO.IN,pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.E2B,GPIO.IN,pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(self.E1A, GPIO.BOTH, callback=self.myCallBack1)
        #GPIO.add_event_detect(self.E1B, GPIO.BOTH, callback=self.myCallBack1)
        GPIO.add_event_detect(self.E2A, GPIO.BOTH, callback=self.myCallBack2)
        #GPIO.add_event_detect(self.E2B, GPIO.BOTH, callback=self.myCallBack2)
    def GetValues(self):
        return self.spin_count1,self.spin_count2
              
    def myCallBack1(self, channel):
        """
        Callback für Encoder 1 (Motor 1).
        Prüft Signal A und B, um die Drehrichtung zu bestimmen.
        """
        current_time = time.time()
        if current_time - self.last_time1 < self.debounce_time:
            return  # Ignoriere dieses Ereignis (Entprellung)
        self.last_time1 = current_time
        A = GPIO.input(self.E1A)  # Zustand von Signal A
        B = GPIO.input(self.E1B)  # Zustand von Signal B

        # Bestimme die Drehrichtung anhand der Phasenverschiebung
        if A != B:  # Signal A kommt vor B
            self.spin_count1 += 1  # Vorwärts
        else:  # Signal B kommt vor A
            self.spin_count1 -= 1  # Rückwärts

    def myCallBack2(self, channel):
        """
        Callback für Encoder 2 (Motor 2).
        Funktioniert analog zu myCallBack1.
        """
        current_time = time.time()
        if current_time - self.last_time2 < self.debounce_time:
            return  # Ignoriere dieses Ereignis (Entprellung)
        self.last_time2 = current_time
        A = GPIO.input(self.E2A)  # Zustand von Signal A
        B = GPIO.input(self.E2B)  # Zustand von Signal B

        if A != B:
            self.spin_count2 += 1  # Vorwärts
        else:
            self.spin_count2 -= 1  # Rückwärts








