from pynput import keyboard,mouse
from typing import override
import serial
import time


class Tracking:
    Pressed = 257
    Released = 260
    Hotkey = 119 #F8

    def __init__(self,controller : Controller) -> None:
        self.controller = controller

    def win32_event_filter(self,msg,data):
        # return True ie input is processed
        # return False ie input is not processed
        return not self.controller.suppress_state

     
class KeyboardTracking(Tracking):

    def __init__(self,controller) -> None:
        super().__init__(controller)

    def on_press(self,key):
        print(str(key))

    def on_release(self,key):
        pass

    # Values for MSLLHOOKSTRUCT.vkCode and kdbllhookstruct can be found here:
    # https://docs.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes
    # https://learn.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-kbdllhookstruct
    # listener._suppress is internally used by suppress() function so dynamic manipulation possible
    # essentially to mimic stopping the listener
    @override
    def win32_event_filter(self,msg,data):
        #print("Key Pressed" if msg == Key.Pressed else "Key Released" + f"keycode: {str(KeyCode.from_vk(data.vkCode))}" )
        if msg == Tracking.Pressed and data.vkCode == Tracking.Hotkey:
            print("HotKey Triggered")
            self.controller.toggle()
        
        # return True ie input is processed by listener
        # return False ie input is not processed by listener
        return not self.controller.suppress_state
    
    def start(self):        
        self.listener = keyboard.Listener(on_press=self.on_press,on_release=self.on_release,suppress=False,win32_event_filter=self.win32_event_filter)
        self.listener.start()




class MouseTracking(Tracking):

    def __init__(self, controller: Controller) -> None:
        super().__init__(controller)

    def on_move(self,x,y):
        print((x,y))

    def on_click(self,x,y,button,pressed):
        print((x,y), button, pressed)

    def on_scroll(self,x,y,dx,dy):
        print((x,y), (dx,dy))

    def start(self):
        self.listener = mouse.Listener(on_move=self.on_move,on_click=self.on_click,on_scroll=self.on_scroll,suppress=False,win32_event_filter=self.win32_event_filter)
        self.listener.start()
    

class Controller():
    def __init__(self,port) -> None:
        self.keyboard = KeyboardTracking(self)
        self.mouse = MouseTracking(self)
        self.suppress_state = False #Intial State

    def start(self):
        self.keyboard.start()
        self.mouse.start()

    def toggle(self):
        self.suppress_state = not self.suppress_state
        self.keyboard.listener._suppress = self.suppress_state

        #NOTE This will block the OS from access mouse events on toggle, for testing purpose keep it commented
        #self.mouse.listener._suppress = self.suppress_state 

    def sendData(self):
        pass

#NOTE change this, make it so that it gets the port right, maybe user input 
if __name__ == "__main__":
    obj = Controller("COM4")
    obj.start()
    while True:
        time.sleep(1)


    
