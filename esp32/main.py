import time
import machine # type: ignore

from serialModule import SerialModule
from bleModule import BleModule


class Bridge():
    def __init__(self) -> None:
        self.serialClient = SerialModule()
        self.bleClient = BleModule()
        self.led = machine.Pin(2,machine.Pin.OUT)

    def main(self):
        while True:
            if not self.bleClient.isConnected():
                self.led.on() #starting connection
                self.bleClient.connect() #blocking event
                self.led.off()

            if self.serialClient.isDataAvailable():
                self.bleClient.sendReport(self.serialClient.report)
                self.serialClient.clear_data()

            
            time.sleep_ms(5) # type: ignore
            

obj = Bridge()
obj.main()