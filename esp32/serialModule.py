import sys
import uselect # pyright: ignore[reportMissingImports]

class SerialModule: 
    def __init__(self):

        #polling object that is gonna check if data avabile to be read at stdin
        self.poll = uselect.poll()
        self.poll.register(sys.stdin, uselect.POLLIN)

        #report will be received from the controller script
        self.report = None
        
    #poll stdin for data if yes then parse it    
    def isDataAvailable(self) -> bool:
        if self.poll.poll(0):
            self.report = sys.stdin.read(8)

        if self.report:
            return True
        
        return False

    def parseData(self,buffer):
        pass

    #reset data
    def clear_data(self):
        self.report = None

            
        
        