from pyPS4Controller.controller import Controller

class MyController(Controller):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_x_press(self):
        print("X button pressed")

    def on_x_release(self):
        print("X button released")

    def on_triangle_press(self):
        print("Triangle button pressed")

    def on_triangle_release(self):
        print("Triangle button released")

    def on_left_arrow_press(self):
        print("Left arrow pressed")

    def on_left_arrow_release(self):
        print("Left arrow released")

    def on_R2_press(self, value):
        print(f"R2 button pressed with intensity: {value}")

    def on_R2_release(self):
        print("R2 button released")

    def on_L3_up(self, value):
        print(f"L3 joystick moved up with intensity: {value}")

    def on_L3_down(self, value):
        print(f"L3 joystick moved down with intensity: {value}")

# Controller-Instanz erstellen und starten
controller = MyController(interface="/dev/input/js0", connecting_using_ds4drv=False)
controller.listen()


