from pynput import keyboard,mouse
from pynput.keyboard import KeyCode,Key
from typing import override
import serial
import time

KEYCODES = {
    # Letters
    "a": (0, 0x04), "b": (0, 0x05), "c": (0, 0x06),
    "d": (0, 0x07), "e": (0, 0x08), "f": (0, 0x09),
    "g": (0, 0x0A), "h": (0, 0x0B), "i": (0, 0x0C),
    "j": (0, 0x0D), "k": (0, 0x0E), "l": (0, 0x0F),
    "m": (0, 0x10), "n": (0, 0x11), "o": (0, 0x12),
    "p": (0, 0x13), "q": (0, 0x14), "r": (0, 0x15),
    "s": (0, 0x16), "t": (0, 0x17), "u": (0, 0x18),
    "v": (0, 0x19), "w": (0, 0x1A), "x": (0, 0x1B),
    "y": (0, 0x1C), "z": (0, 0x1D),

    # Numbers
    "1": (0, 0x1E),
    "2": (0, 0x1F),
    "3": (0, 0x20),
    "4": (0, 0x21),
    "5": (0, 0x22),
    "6": (0, 0x23),
    "7": (0, 0x24),
    "8": (0, 0x25),
    "9": (0, 0x26),
    "0": (0, 0x27),

    # Normal symbols
    "\n": (0, 0x28),  # Enter
    "\b": (0, 0x2A),  # Backspace
    "\t": (0, 0x2B),  # Tab
    " ":  (0, 0x2C),  # Space
    "-":  (0, 0x2D),
    "=":  (0, 0x2E),
    "[":  (0, 0x2F),
    "]":  (0, 0x30),
    "\\": (0, 0x31),
    ";":  (0, 0x33),
    "'":  (0, 0x34),
    "`":  (0, 0x35),
    ",":  (0, 0x36),
    ".":  (0, 0x37),
    "/":  (0, 0x38),

    # Shift + number
    "!": (1, 0x1E),  # Shift + 1
    "@": (1, 0x1F),  # Shift + 2
    "#": (1, 0x20),  # Shift + 3
    "$": (1, 0x21),  # Shift + 4
    "%": (1, 0x22),  # Shift + 5
    "^": (1, 0x23),  # Shift + 6
    "&": (1, 0x24),  # Shift + 7
    "*": (1, 0x25),  # Shift + 8
    "(": (1, 0x26),  # Shift + 9
    ")": (1, 0x27),  # Shift + 0

    # Shift + symbols
    "_":  (1, 0x2D),  # Shift + -
    "+":  (1, 0x2E),  # Shift + =
    "{":  (1, 0x2F),  # Shift + [
    "}":  (1, 0x30),  # Shift + ]
    "|":  (1, 0x31),  # Shift + \
    ":":  (1, 0x33),  # Shift + ;
    "\"": (1, 0x34),  # Shift + '
    "~":  (1, 0x35),  # Shift + `
    "<":  (1, 0x36),  # Shift + ,
    ">":  (1, 0x37),  # Shift + .
    "?":  (1, 0x38),  # Shift + /
}

def get_hid_code(char):
    shift = False
    print(char)
    if ord("A") <= ord(char) <= ord("Z"):
        shift = True
    char = char.lower()
    if char in KEYCODES:
        return (KEYCODES[char][0] | shift,KEYCODES[char][1])

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

    def on_press(self,key : Key):
        print(str(key))
        print(key.value)
        
        # try: 
        #     char = key.char
        # except AttributeError:
        #     modi = 
        #update the keyboard state and send it che
        
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
        self.modifiers  = {"cmd":0, "alt_gr":0, "shift_r":0, "ctrl_r":0, "menu":0, "alt_l":0, "shift":0, "ctrl_l":0}
        self.keypresses = [0]*6

    def start(self):
        self.keyboard.start()
        self.mouse.start()

    def toggle(self):
        self.suppress_state = not self.suppress_state
        self.keyboard.listener._suppress = self.suppress_state

        #NOTE This will block the OS from access mouse events on toggle, for testing purpose keep it commented
        #self.mouse.listener._suppress = self.suppress_state 

    def updateState(self):
        pass

#NOTE change this, make it so that it gets the port right, maybe user input 
if __name__ == "__main__":
    obj = Controller("COM4")
    obj.start()
    while True:
        time.sleep(1)


    
