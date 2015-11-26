class IRLineObject():

    def __init__(self, line, lineNum=-1):
        self.line = line
        self.Regs = []
        self.op = ""
        self.newLine = line
        self.assignVariables()
        self.lineNum = lineNum

    def assignVariables(self):
        self.lineSplit = self.line.rstrip().split(" ")
        self.op = self.lineSplit[0]
        for i in self.lineSplit:
            if i.startswith("$T"):
                self.Regs.append(i)

    def updateLine(self, reg, newReg):
        self.line = self.line.replace(reg, newReg, 1)
        #numReg = self.Regs.count(reg)
        #for i in range(0, numReg):
        self.Regs = [x if (x != reg) else newReg for x in self.Regs]

    def removeTemp(self, reg, replacement):
        self.lineSplit[2] = replacement
        self.line = " ".join(self.lineSplit)
        # self.line = self.line.replace(reg, replacement)
        self.Regs.remove(reg)


class IRLinesArray():

    def createIRString(IRLines):
        newIR = ""
        for i in IRLines:
            newIR = newIR + i.line + "\n"

        return newIR

    def CreateLineObjects(strLines):
        IRLines = []
        count = 0
        for line in strLines:
            IRLines.append(IRLineObject(line, count))
            count += 1
        return IRLines



class OpDefinitions():
    comparisonOps = ["GEI", "GEF", "LEI", "LEF", "LTI", "LTF", "GTI", "GTF", "EQI", "EQF", "NEI", "NEF"]
    unconditionalJumpOps = ["JUMP", "JSR"]    
    mathIntOps   = ["ADDI", "SUBI", "MULTI", "DIVI"]
    mathFloatOps = ["ADDD", "SUBF", "MULTF", "DIVF"]
