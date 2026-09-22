from pynput import keyboard,mouse
import serial

class KeyboardTracking():
    def on_press(self,key):
        print(str(key))

    def on_release(self,key):
        pass

    def start(self):
        self.listener = keyboard.Listener(on_press=self.on_press,on_release=self.on_release)
        self.listener.start()

class MouseTracking():
    def on_move(self,x,y):
        print((x,y))

    def on_click(self,x,y,button,pressed):
        print((x,y), button, pressed)

    def on_scroll(self,x,y,dx,dy):
        print((x,y), (dx,dy))

    def start(self):
        self.listener = mouse.Listener(on_move=self.on_move,on_click=self.on_click,on_scroll=self.on_scroll)
        self.listener.start()
    

class Controller():
    def __init__(self,COM) -> None:
        self.ser = serial.Serial()
        self.keyboard = KeyboardTracking()
        self.mouse = MouseTracking()
        self.keys = []
        self.coords = []

    def start(self):
        self.keyboard.start()
        self.mouse.start()

    def sendData(self):
        pass

obj = Controller(4)
obj.start()