import sys
import uselect # pyright: ignore[reportMissingImports]


class SerialModule: 
    def __init__(self):

        #polling object that is gonna check if data avabile to be read at stdin
        self.poll = uselect.poll()
        self.poll.register(sys.stdin, uselect.POLLIN)

        self.data = None
        self.modifiers  = {"rgui":0, "ralt":0, "rshift":0, "rctrl":0, "lgui":0, "lalt":0, "lshift":0, "lctrl":0}


    #poll stdin for data if yes then parse it    
    def isDataAvailable(self) -> bool:
        buffer = None
        if self.poll.poll(0):
            buffer = sys.stdin.readline().strip().split("-t")
            buffer.append("")
        #if data exists parse it
        if buffer:
            self.parseData(buffer)
            return True
        
        return False

    def parseData(self,buffer):
        self.data = buffer[0]
        for s in buffer[1].strip().lower().split():
            if s in self.modifiers:
                self.modifiers[s] = 1

    #reset data
    def clear_data(self):
        for key in self.modifiers:
            self.modifiers[key] = 0

            
        
        