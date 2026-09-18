from serial import SerialModule
from ble import BLE_MODULE

class Controller():
    def __init__(self) -> None:
        self.serialClient = SerialModule()
        self.bleClient = BLE_MODULE()

    def main(self):
        while True:
            if not self.bleClient.isConnected():
                self.bleClient.connect()

            if self.serialClient.isDataAvailable():
                self.bleClient.recieve_data(self.serialClient.data,self.serialClient.modifiers)
                self.serialClient.clear_data()
                print("> ",end="")



obj = Controller()
obj.main()