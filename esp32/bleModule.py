#check 
#keyboard appearance code = 961 

#target esp32 sends "hello, world!" keystrokes

from hid_services import MyHID,Keyboard
from hid_keystores import NVSKeyStore
import time

class BleModule:
    def __init__(self,name="Bluetooth KBM",apperance=961):

        self.KBM = MyHID(name)
        
        #961 = keyboard (org.bluetooth.characteristic.gap.appearance.xml)
        self.KBM.device_appearance = apperance                                             


        self.KBM.set_bonding(True)
        self.KBM.set_le_secure(False)
        self.keystore = NVSKeyStore()
        #self.keystore.clear_secrets()
        self.KBM.set_keystore(self.keystore)

        #callback fn called by the lib when state change
        self.KBM.set_state_change_callback(self.keyboard_state_callback)                   

        #overwrite this implementation for changing advertisment characteristics
        self.KBM.start()                                                                   
        
        
    def keyboard_state_callback(self):
        if self.KBM.get_state() is Keyboard.DEVICE_IDLE:
            return
        elif self.KBM.get_state() is Keyboard.DEVICE_ADVERTISING:
            return
        elif self.KBM.get_state() is Keyboard.DEVICE_CONNECTED:
            return
        else: #Keyboard.DEVICE_STOPPED
            return

    def isConnected(self):
        return self.KBM.get_state() is Keyboard.DEVICE_CONNECTED

    def connect(self):
        print("Establishing Connection...")
            #start ble advertisment  with timeout 30s
        while not self.isConnected():
            if self.KBM.get_state() is Keyboard.DEVICE_IDLE:           
                self.KBM.start_advertising()                                               
                timeout = 30                                                                         
                while timeout > 0:
                    state = self.KBM.get_state()

                    if state is Keyboard.DEVICE_CONNECTED:
                        print("Device Connected")
                        return 

                    if state is not Keyboard.DEVICE_ADVERTISING:
                        break

                    time.sleep(1)
                    timeout -= 1

                #timeout stop advertising
                if not self.isConnected():                                                                           
                    self.KBM.stop_advertising()
                    print("Connection Failed, try again")
                    time.sleep(2) #wait 2 seconds before trying again

            elif self.KBM.get_state() is Keyboard.DEVICE_STOPPED:
                print("Device Stopped")
                return
            
    # def self_test(self):
    #     self.sendReport(bytes([0x02, 0, 10, 0, 0]))            # mouse nudge right
    #     time.sleep_ms(500)
    #     self.sendReport(bytes([0x01, 0, 0, 0x04, 0, 0, 0, 0, 0]))  # press 'a'
    #     time.sleep_ms(50)
    #     self.sendReport(bytes([0x01] + [0] * 8))                # release
        
    def sendReport(self,report):
        if self.isConnected():
            report_header = report[0]
            report = report[1::]
            if report_header == 0x01:   #Keyboard report
                self.KBM.notify_hid_report(report)
            elif report_header == 0x02: #Mouse report
                self.KBM.notify_mouse_report(report)
