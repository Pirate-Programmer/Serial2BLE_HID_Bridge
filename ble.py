#check 
#keyboard appearance code = 961 

#target esp32 sends "hello, world!" keystrokes

from hid_services import Keyboard
import time

#keycodes mentioned at https://www.usb.org/sites/default/files/hut1_7.pdf  (under Keyboard/Keypad Page)
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

class BLE_MODULE:
    def __init__(self,name="Keyboard",apperance=961):
        
        #my ble hid
        self.keyboard = Keyboard(name)
        #961 = keyboard (org.bluetooth.characteristic.gap.appearance.xml)
        self.keyboard.device_appearance = apperance                                             

        self.keyboard.set_bonding(False)
        self.keyboard.set_le_secure(False)

        #callback fn called by the lib when state change
        self.keyboard.set_state_change_callback(self.keyboard_state_callback)                   

        #overwrite this implementation for changing advertisment characteristics
        self.keyboard.start()                                                                   
        
        
    def keyboard_state_callback(self):
        if self.keyboard.get_state() is Keyboard.DEVICE_IDLE:
            return
        elif self.keyboard.get_state() is Keyboard.DEVICE_ADVERTISING:
            return
        elif self.keyboard.get_state() is Keyboard.DEVICE_CONNECTED:
            return
        else: #Keyboard.DEVICE_STOPPED
            return

    def isConnected(self):
        return self.keyboard.get_state() is Keyboard.DEVICE_CONNECTED

    def connect(self):
        print("Establishing Connection...")
            #start ble advertisment  with timeout 30s
        if self.keyboard.get_state() is Keyboard.DEVICE_IDLE:           
            self.keyboard.start_advertising()                                               
            timeout = 30                                                                         
            while timeout > 0:
                state = self.keyboard.get_state()

                if state is Keyboard.DEVICE_CONNECTED:
                    print("Device Connected")
                    return 

                if state is not Keyboard.DEVICE_ADVERTISING:
                    return

                time.sleep(1)
                timeout -= 1

            #timeout stop advertising
            if self.keyboard.get_state() is not Keyboard.DEVICE_CONNECTED:                                                                           
                self.keyboard.stop_advertising()
                print("Connection Failed, try again")

        elif self.keyboard.get_state() is Keyboard.DEVICE_STOPPED:
            print("Device Stopped")


    def type_char(self, char : str) -> None:                                                          
        mod = 0
        code = 0
        if "A" <= char <= "Z":
            mod = 1
        
        char = char.lower()
        if char not in KEYCODES:
            print("not supported")
            return

        #press the keys
        modi,code = KEYCODES[char]
        mod = mod | modi
        self.keyboard.set_keys(code)                                                                                                                     
        self.keyboard.set_modifiers(lshift=mod)
        self.keyboard.notify_hid_report()
        time.sleep_ms(25) # type: ignore

        #release the keys 
        self.keyboard.set_keys()                                                                                                                        
        self.keyboard.set_modifiers()
        self.keyboard.notify_hid_report()
        time.sleep_ms(25) # type: ignore

    def type_string(self,data):
        for word in data.split():
            for char in word:
                self.type_char(char)
            

    def recieve_data(self,data,modifiers):
        self.keyboard.set_modifiers(**modifiers)
        self.type_string(data)
        
            



