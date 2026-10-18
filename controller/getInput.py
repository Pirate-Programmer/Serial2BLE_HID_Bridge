from pynput import keyboard,mouse
from pynput.keyboard import KeyCode,Key
from pynput.mouse import Button
from typing import override
import serial
import time
import threading

#keycodes mentioned at https://www.usb.org/sites/default/files/hut1_7.pdf  (under Keyboard/Keypad Page)
KEYCODES = {
    # Letters
    "a": 0x04, "b": 0x05, "c": 0x06,
    "d": 0x07, "e": 0x08, "f": 0x09,
    "g": 0x0A, "h": 0x0B, "i": 0x0C,
    "j": 0x0D, "k": 0x0E, "l": 0x0F,
    "m": 0x10, "n": 0x11, "o": 0x12,
    "p": 0x13, "q": 0x14, "r": 0x15,
    "s": 0x16, "t": 0x17, "u": 0x18,
    "v": 0x19, "w": 0x1A, "x": 0x1B,
    "y": 0x1C, "z": 0x1D,

    # Numbers
    "1": 0x1E, "2": 0x1F, "3": 0x20,
    "4": 0x21, "5": 0x22, "6": 0x23,
    "7": 0x24, "8": 0x25, "9": 0x26,
    "0": 0x27,

    # Basic keys
    Key.enter: 0x28,
    Key.esc: 0x29,
    Key.backspace: 0x2A,
    Key.tab: 0x2B,
    Key.space: 0x2C,
    Key.caps_lock: 0x39,

    # Symbols
    "-": 0x2D, "=": 0x2E, "[": 0x2F,
    "]": 0x30, "\\": 0x31, ";": 0x33,
    "'": 0x34, "`": 0x35, ",": 0x36,
    ".": 0x37, "/": 0x38,

    #Shift Symbols
    "!": 0x1E, "@": 0x1F, "#": 0x20,
    "$": 0x21, "%": 0x22, "^": 0x23,
    "&": 0x24, "*": 0x25, "(": 0x26,
    ")": 0x27,

    "_": 0x2D, "+": 0x2E, "{": 0x2F,
    "}": 0x30, "|": 0x31, ":": 0x33,
    '"': 0x34, "~": 0x35, "<": 0x36,
    ">": 0x37, "?": 0x38,

    # Function keys
    Key.f1: 0x3A, Key.f2: 0x3B, Key.f3: 0x3C,
    Key.f4: 0x3D, Key.f5: 0x3E, Key.f6: 0x3F,
    Key.f7: 0x40, Key.f8: 0x41, Key.f9: 0x42,
    Key.f10: 0x43, Key.f11: 0x44, Key.f12: 0x45,

    # Navigation
    Key.print_screen: 0x46,
    Key.scroll_lock: 0x47,
    Key.pause: 0x48,
    Key.insert: 0x49,
    Key.home: 0x4A,
    Key.page_up: 0x4B,
    Key.delete: 0x4C,
    Key.end: 0x4D,
    Key.page_down: 0x4E,

    # Arrow keys
    Key.right: 0x4F, Key.left: 0x50,
    Key.down: 0x51, Key.up: 0x52,
}

MODIFIERS = {
    Key.ctrl_l:  0x01,
    Key.shift:   0x02,
    Key.alt_l:   0x04,
    Key.cmd:     0x08,
    Key.ctrl_r:  0x10,
    Key.shift_r: 0x20,
    Key.alt_gr:  0x40,
}


MOUSE_BUTTONS = {
    Button.left:   0x01,  # Bit 0
    Button.right:  0x02,  # Bit 1
    Button.middle: 0x04,  # Bit 2
    Button.x1:     0x08,  # Bit 3
    Button.x2:     0x10,  # Bit 4
}

class Tracking:
    Pressed = 257
    Released = 260
    Hotkey = 119 #F8

    def __init__(self,controller : Controller) -> None:
        self.controller = controller

    def win32_event_filter(self,msg,data):
        # return True ie input is processed
        # return False ie input is not processed
        return self.controller.suppress_state

     
class KeyboardTracking(Tracking):

    def __init__(self,controller) -> None:
        super().__init__(controller)
        self.con = controller

    def on_press(self, key):
        if key in MODIFIERS:
            self.con.modifier |= MODIFIERS[key]
            self.con.keycode = 0

        elif key in KEYCODES: #true when key is of type Key (pynput)
            self.con.keycode = KEYCODES[key]

        elif isinstance(key, KeyCode) and key.char:
            char = key.char
            if char in KEYCODES:
                self.con.keycode = KEYCODES[char.lower()]

        self.con.send_report(self.con.create_keyboard_hid_report())

    def on_release(self,key):
        print(str(key))
        if key in MODIFIERS:
            self.con.modifier &= ~MODIFIERS[key]
        else:
            self.con.keycode = 0
        self.con.send_report(self.con.create_keyboard_hid_report())
    
    # Values for MSLLHOOKSTRUCT.vkCode and kdbllhookstruct can be found here:
    # https://docs.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes
    # https://learn.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-kbdllhookstruct
    # listener._suppress is internally used by suppress() function so during runtime manipulation possible
    # essentially to mimic stopping the listener
    @override
    def win32_event_filter(self,msg,data):
        #print("Key Pressed" if msg == Key.Pressed else "Key Released" + f"keycode: {str(KeyCode.from_vk(data.vkCode))}" )
        if msg == Tracking.Pressed and data.vkCode == Tracking.Hotkey:
            print("HotKey Triggered")
            self.controller.toggle()
        
        # return True ie input is processed by listener
        # return False ie input is not processed by listener
        return  self.controller.suppress_state
    
    def start(self):        
        self.listener = keyboard.Listener(on_press=self.on_press,on_release=self.on_release,suppress=False,win32_event_filter=self.win32_event_filter)
        self.listener.start()

    def stop(self):
        self.listener.stop()

class MouseTracking(Tracking):

    def __init__(self, controller: Controller) -> None:
        super().__init__(controller)
        self.buttons = 0
        self.prev_x = None
        self.prev_y = None
        self.acc_dx = self.acc_dy = 0


    def on_move(self, x, y):
        if self.prev_x is None:
            self.prev_x, self.prev_y = x, y
            return
        self.acc_dx += x - self.prev_x
        self.acc_dy += y - self.prev_y
        self.prev_x, self.prev_y = x, y

    def _pump(self):
        while self.controller.running:
            time.sleep(0.01)
            dx = max(-127, min(127, int(self.acc_dx)))
            dy = max(-127, min(127, int(self.acc_dy)))
            self.acc_dx -= dx
            self.acc_dy -= dy
            if dx or dy:
                self.controller.send_report(
                    self.controller.create_mouse_hid_report(self.buttons, dx, dy))
    
    def on_click(self,x,y,button,pressed):
        #print((x,y), button, pressed)
        mask = MOUSE_BUTTONS.get(button,0)
        if not mask:
            return

        if pressed: 
            self.buttons |= mask     # sets the bit
        else:
            self.buttons &= ~mask   # clears the bit

        self.controller.send_report(self.controller.create_mouse_hid_report(buttons=self.buttons))

    def on_scroll(self,x,y,dx,dy):
        #print((x,y), (dx,dy))
        if dy:
            self.controller.send_report(self.controller.create_mouse_hid_report(buttons=self.buttons,wheel=dy))

    def start(self):
        threading.Thread(target=self._pump, daemon=True).start()
        self.listener = mouse.Listener(on_move=self.on_move,on_click=self.on_click,on_scroll=self.on_scroll,suppress=False,win32_event_filter=self.win32_event_filter)
        self.listener.start()
    
    def stop(self):
        self.listener.stop()


class Controller():
    KEYBOARD_HEADER = 0x01
    MOUSE_HEADER = 0x02
    def __init__(self,port="COM4",baudrate=115200) -> None:
        #Initialize serial communication
        self.ser = serial.Serial()
        self.ser.port = port
        self.ser.baudrate = baudrate
        self.ser.timeout = 0
        self.ser.dtr = False
        self.ser.rts = False
        self.ser.open()

        self.keyboard = KeyboardTracking(self)
        self.mouse = MouseTracking(self)
        self.suppress_state = False #Intial State
        self.running = True #controller state
        self.modifier = 0
        self.keycode = 0

        self.lock = threading.Lock()

    def start(self):
        self.keyboard.start()
        self.mouse.start()

    #release all the keys, close serial communication and stop the listeners
    def stop(self):
        self.running = False
        self.keyboard.stop()
        self.mouse.stop()

        self.ser.write(bytes([1]) + bytes(8))   # release keys
        self.ser.write(bytes([2]) + bytes(4))   # release mouse
        self.ser.close() 
        

    def toggle(self):
        self.suppress_state = not self.suppress_state
        self.keyboard.listener._suppress = self.suppress_state

        #NOTE This will block the OS from access mouse events on toggle, for testing purpose keep it commented
        self.mouse.listener._suppress = self.suppress_state 
        
    def create_keyboard_hid_report(self,modifier=None,keycode=None) -> bytes:
        if keycode is None:
            keycode = self.keycode
        if modifier is None:
            modifier = self.modifier
        
        return bytes([Controller.KEYBOARD_HEADER]) + bytes(
            [
            modifier,                          # Modifier byte
            0x00,                              # reserved
            keycode,                           # key slot 1
            0x00,0x00,0x00,0x00,0x00           # remaining 5 key slots
            ])



    def create_mouse_hid_report(self,buttons,dx=0,dy=0,wheel=0):
        dx = max(-127,min(127,dx))
        dy = max(-127,min(127,dy))
        wheel = max(-127,min(127,wheel))
        
        
        return bytes([Controller.MOUSE_HEADER]) + bytes(
            [
                buttons & 0x1F,               # Mouse button state
                dx & 0xFF,                    # relative x coord
                dy & 0xFF,                    # relative y coord
                wheel & 0xFF                  # relative scroll ie in y direction
            ])

    def send_report(self, report: bytes):
        with self.lock:
            self.ser.write(report)
    

#NOTE change this, make it so that it gets the port right, maybe user input 
if __name__ == "__main__":
    obj = Controller("COM4")
    try:
        obj.start()
        threading.Event().wait() #preventing main theard from exiting

    except KeyboardInterrupt:
        print("Stopping controller...")

    finally:
        obj.stop()
        print("Controller stopped exiting...")


    
