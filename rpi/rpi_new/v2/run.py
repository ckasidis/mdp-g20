from interfaces import *
import sys
class Task1():
    def __init__(self):
        self.AND = Android()
        self.ALG = Algo()
        self.STM = STM()
        self.IMREC = IMAGEREC()

    def run(AND, ALG, STM, IMREC):
        self.AND.connect_AND()
        self.ALG.connect_ALG()
        self.STM.connect_STM()
                
        path = self.AND.read_from_AND()
        self.ALG.write_to_ALG(path)

        cmds = self.ALG.read_from_ALG()
        cmds = cmds.split(',')
        print("Commands are:",cmds)

        for i in cmds:
            if i=='RPI|TOCAM':
                response = self.IMREC.takePic()
                if response:
                    and_msg = 'OBS-'+''+int(response)
                    self.AND.write_to_AND(and_msg)
            elif 'STM|' in i:
                msgs = i.split('|',1)
                msg = msgs[1]
                self.STM.move(msg)
            elif 'RPI_END' in i:
                sys.exit()