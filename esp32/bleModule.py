#check 
#keyboard appearance code = 961 

#target esp32 sends "hello, world!" keystrokes

from hid_services import Keyboard
import time

class BleModule:
    def __init__(self,name="Keyboard",apperance=961):

        self.keyboard = Keyboard(name)
        
        #961 = keyboard (org.bluetooth.characteristic.gap.appearance.xml)
        self.keyboard.device_appearance = apperance                                             

        #NOTE change this for secure connection
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
        while not self.isConnected():
            if self.keyboard.get_state() is Keyboard.DEVICE_IDLE:           
                self.keyboard.start_advertising()                                               
                timeout = 30                                                                         
                while timeout > 0:
                    state = self.keyboard.get_state()

                    if state is Keyboard.DEVICE_CONNECTED:
                        print("Device Connected")
                        return 

                    if state is not Keyboard.DEVICE_ADVERTISING:
                        break

                    time.sleep(1)
                    timeout -= 1

                #timeout stop advertising
                if not self.isConnected():                                                                           
                    self.keyboard.stop_advertising()
                    print("Connection Failed, try again")
                    time.sleep(2) #wait 2 seconds before trying again

            elif self.keyboard.get_state() is Keyboard.DEVICE_STOPPED:
                print("Device Stopped")
                return

    def sendReport(self,report):
        if len(report) == 8:
            self.keyboard.notify_hid_report(report)
    
            



