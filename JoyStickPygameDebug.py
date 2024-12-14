import pygame
import time

#Installed DS4Windows now it works great

def main():
    # Initialize Pygame
    pygame.init()
    pygame.joystick.init()

    # Get the number of joysticks
    joystick_count = pygame.joystick.get_count()
    
    print(f"Number of joysticks detected: {joystick_count}")

    # Iterate through all detected joysticks
    for i in range(joystick_count):
        joystick = pygame.joystick.Joystick(i)
        joystick.init()
        
        print(f"\n--- Joystick {i} Details ---")
        print(f"Name: {joystick.get_name()}")
        print(f"Number of Axes: {joystick.get_numaxes()}")
        print(f"Number of Buttons: {joystick.get_numbuttons()}")
        print(f"Number of Hats: {joystick.get_numhats()}")

    # Main event loop to keep window open and process events
    try:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                
                # Optional: Print out events if you want to see controller interactions
                if event.type == pygame.JOYBUTTONDOWN:
                    print(f"Button {event.button} pressed")
                elif event.type == pygame.JOYAXISMOTION:
                    print(f"Axis {event.axis} moved to {event.value}")
            
            time.sleep(0.1)  # Prevent high CPU usage
    except KeyboardInterrupt:
        pass
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()