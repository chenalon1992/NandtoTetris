"""
This file consists of a VMWriter object which hold the VM written array
 and all writing methods
"""


"""
VMWriter class as described above
"""


class VMWriter:

    """
    Constructor for VMWriter, hold the written VM file as an array
    """
    def __init__(self):
        self.VMArray = []

    def writePush(self, segment, index):
        VMCommandStr = 'push ' + segment + ' ' + str(index) + '\n'
        self.VMArray.append(VMCommandStr)

    def writePop(self, segment, index):
        VMCommandStr = 'pop ' + segment + ' ' + str(index) + '\n'
        self.VMArray.append(VMCommandStr)

    def writeArithmetic(self, command):
        VMCommandStr = command + '\n'
        self.VMArray.append(VMCommandStr)

    def writeLabel(self, label):
        VMCommandStr = 'label ' + label + '\n'
        self.VMArray.append(VMCommandStr)

    def writeGoto(self, label):
        VMCommandStr = 'goto ' + label + '\n'
        self.VMArray.append(VMCommandStr)

    def writeIf(self, label):
        VMCommandStr = 'if-goto ' + label + '\n'
        self.VMArray.append(VMCommandStr)

    def writeCall(self, name, nArgs):
        VMCommandStr = 'call ' + name + ' ' + str(nArgs) + '\n'
        self.VMArray.append(VMCommandStr)

    def writeFunction(self, name, nLocals):
        VMCommandStr = 'call ' + name + ' ' + str(nLocals) + '\n'
        self.VMArray.append(VMCommandStr)

    def writeReturn(self):
        VMCommandStr = 'return\n'
        self.VMArray.append(VMCommandStr)
