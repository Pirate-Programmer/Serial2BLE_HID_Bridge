import time

from serialModule import SerialModule
from bleModule import BleModule

class Bridge():
    def __init__(self) -> None:
        self.serialClient = SerialModule()
        self.bleClient = BleModule()

    def main(self):
        while True:
            if not self.bleClient.isConnected():
                self.bleClient.connect()
                #print("> ",end="")

            if self.serialClient.isDataAvailable():
                self.bleClient.recieve_data(self.serialClient.data,self.serialClient.modifiers)
                self.serialClient.clear_data()
                #print("> ",end="")

            time.sleep_ms(10) # type: ignore

obj = Bridge()
obj.main()