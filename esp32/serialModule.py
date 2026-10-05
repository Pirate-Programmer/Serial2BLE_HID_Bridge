import sys
import uselect # pyright: ignore[reportMissingImports]
from collections import deque




class SerialModule: 
    def __init__(self):

        #polling object that is gonna check if data avabile to be read at stdin
        self.poll = uselect.poll()
        self.poll.register(sys.stdin, uselect.POLLIN)

        self.MAX_QUEUE_LEN = 20
        self.data = deque([], self.MAX_QUEUE_LEN)
        #NOTE test this with diff keyboard cause cmd and menu is defo different for diff keyboards
        self.modifiers  = {"cmd":0, "alt_gr":0, "shift_r":0, "ctrl_r":0, "menu":0, "alt_l":0, "shift":0, "ctrl_l":0}


    #poll stdin for data if yes then parse it    
    def isDataAvailable(self) -> bool:
        buffer = None
        if self.poll.poll(0):
            buffer = sys.stdin.read(1)

        #if data exists parse it
        if buffer:
            self.data.append(buffer)
            return True
        
        return False

    def parseData(self,buffer):
        pass

    #reset data
    def clear_data(self):
        pass

            
        
        