import sys
import uselect # type: ignore
import micropython # type: ignore

class SerialModule:
    FRAME_LEN = {0x01: 9, 0x02: 5} #Keyboard or mouse header len

    def __init__(self):
        #micropython.kbd_intr(-1)      # stop 0x03 bytes from raising KeyboardInterrupt
        self.poll = uselect.poll()
        self.poll.register(sys.stdin, uselect.POLLIN)
        self.buff = bytearray()
        self.report = None

    def isDataAvailable(self) -> bool:
        # drain whatever has arrived
        while self.poll.poll(0):
            b = sys.stdin.buffer.read(1)
            if not b:
                break
            self.buff += b

        # extract one complete frame, resyncing on bad headers
        while self.buff:
            need = self.FRAME_LEN.get(self.buff[0])
            if need is None:
                self.buff = self.buff[1:]        # junk byte, drop it
                continue
            if len(self.buff) >= need:
                self.report = bytes(self.buff[:need])
                self.buff = self.buff[need:]
                return True
            break                                 # incomplete, wait for more
        return False

    def clear_data(self):
        self.report = None