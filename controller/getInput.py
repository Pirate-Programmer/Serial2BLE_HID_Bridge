from pynput import keyboard

class Controller:
    def __init__(self,COM) -> None:
        self.COM = COM
        