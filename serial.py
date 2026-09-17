import sys
import uselect # pyright: ignore[reportMissingImports]


class SerialModule: 
    def __init__(self):

        #polling object that is gonna check if data avabile to be read at stdin
        self.poll = uselect.poll()
        self.poll.register(sys.stdin, uselect.POLLIN)

        self.data = None
        self.modifiers  = {"rgui":0, "ralt":0, "rshift":0, "rctrl":0, "lgui":0, "lalt":0, "lt":0, "lctrl":0}

        
    def check_input(self):
        
        if self.poll.poll(0):
            self.data = sys.stdin.readline().strip().split("-t")

        if self.data:
            print(self.data)
            self.data = None
        