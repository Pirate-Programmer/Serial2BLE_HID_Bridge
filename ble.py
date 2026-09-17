#check 
#keyboard appearance code = 961 

#target esp32 sends "hello, world!" keystrokes

from hid_services import Keyboard
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

class BLE_MODULE:
    def __init__(self):
        
        #my ble hid
        self.keyboard = Keyboard("Ear Buds")
        self.keyboard.device_appearance = 961                                                   #961 = keyboard (org.bluetooth.characteristic.gap.appearance.xml)

        self.keyboard.set_bonding(False)
        self.keyboard.set_le_secure(False)
        self.keyboard.set_state_change_callback(self.keyboard_state_callback)                   #callback fn called by the lib when state change

        self.keyboard.start()                                                                   #overwrite this implementation for changing advertisment characteristics
        
        
    def keyboard_state_callback(self):
        if self.keyboard.get_state() is Keyboard.DEVICE_IDLE:
            return
        elif self.keyboard.get_state() is Keyboard.DEVICE_ADVERTISING:
            return
        elif self.keyboard.get_state() is Keyboard.DEVICE_CONNECTED:
            return
        else: #Keyboard.DEVICE_STOPPED
            return



    def start(self):
        while True:

            if self.keyboard.get_state() is Keyboard.DEVICE_IDLE:           
                self.keyboard.start_advertising()                                               #start ble advertisment
                timeout = 30                                                                          #intiate connection timeout 30s
                while timeout > 0:
                    state = self.keyboard.get_state()

                    if state is Keyboard.DEVICE_CONNECTED:
                        print("Device Connected")
                        break

                    if state is not Keyboard.DEVICE_ADVERTISING:
                        break

                    time.sleep(1)
                    timeout -= 1

                if self.keyboard.get_state() is not Keyboard.DEVICE_CONNECTED:                                                                           #connection failed stop advertising
                    self.keyboard.stop_advertising()
                    print("Connection Failed, trying again in 5 seconds")
                    time.sleep(5)

            elif self.keyboard.get_state() is Keyboard.DEVICE_CONNECTED:                        #NOTE change this to accept input from serial module
                while self.keyboard.get_state() is Keyboard.DEVICE_CONNECTED:
                    print("Connection maintained")
                    time.sleep(1)
                    self.temp()
            else:
                print("Device Stopped, exiting...")
                return

    def send_char(self, char : str) -> None:                                                          #keycodes mentioned at https://www.usb.org/sites/default/files/hut1_7.pdf  (under Keyboard/Keypad Page)
        mod = 0
        code = 0
        if "A" <= char <= "Z":
            mod = 1
        
        char = char.lower()
        if char not in KEYCODES:
            print("not supported")
            return


        modi,code = KEYCODES[char]
        mod = mod | modi
        self.keyboard.set_keys(code)                                                        #press the keys                                                             
        self.keyboard.set_modifiers(left_control=1,left_alt=1)
        self.keyboard.notify_hid_report()
        time.sleep_ms(25)
        
        self.keyboard.set_keys()                                                            #release the keys                                                             
        self.keyboard.set_modifiers()
        self.keyboard.notify_hid_report()
        time.sleep_ms(25)



    def temp(self):
        time.sleep(7)
        test = "T"
        for c in test:
            self.send_char(c)
            


obj = BLE_MODULE()
obj.start()
