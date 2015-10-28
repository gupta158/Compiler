from antlr4 import *
from LittleExprParser import LittleExprParser
from LittleExprListener import LittleExprListener
from AST import *

#TODO : a = 20 -> 1 move
#       redundant moves for only 1 temp
class Optimizer():

    def __init__(self, IRcode):
        self.IRcode = IRcode
        self.Regs = {}

    def optimize(self):
        lines = self.IRcode.rstrip().split("\n")
        IRLines = self.CreateLineObjects(lines)
        IRLines = self.checkConstants(IRLines)
        self.markLines(IRLines)
        IRLines = self.simplifyMoves(IRLines)
        self.Regs = {}
        self.markLines(IRLines)
        IRLines = self.reduceRegisters(IRLines)

        #self.printRegs()
        #print(self.createNewIR(IRLines))

        return self.createNewIR(IRLines)


    def CreateLineObjects(self, lines):
        IRLines = []
        count = 0
        for line in lines:
            IRLines.append(IRLine(line, count))
            count += 1
        return IRLines

    def markLines(self, IRlines):
        for IRline in IRlines:
            for reg in IRline.Regs:
                if not reg in self.Regs.keys():
                    self.Regs[reg] = Register(reg, IRline.lineNum, IRline.lineNum)
                self.Regs[reg].lastUsed = IRline.lineNum

    def reduceRegisters(self, IRLines):
        mappingDict = {}
        recycledRegisters = []
        for IRLine in IRLines:
            regArray = IRLine.Regs
            for reg in regArray:
                #print("----------------------------------------------------------------------")
                #print(mappingDict)
                #print(IRLine.line)
                #print(IRLine.lineNum)
                #print(self.Regs[reg].firstUsed)
                #print(reg)
                #print(self.Regs[reg].lastUsed)
                #print(recycledRegisters)
                #print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                if self.Regs[reg].firstUsed == IRLine.lineNum:
                    if len(recycledRegisters) != 0:
                        mappingDict[reg] = recycledRegisters.pop()
                        #self.Regs[mappingDict[reg]].lastUsed = self.Regs[reg].lastUsed 

                elif self.Regs[reg].lastUsed == IRLine.lineNum:
                    if reg in mappingDict.keys():
                        recycledRegisters.append(mappingDict[reg])
                    else:
                        recycledRegisters.append(reg)

                if reg in mappingDict.keys():
                    IRLine.updateLine(reg, mappingDict[reg])
                #print("----------------------------------------------------------------------")
                #print(mappingDict)
                #print(IRLine.line)
                #print(recycledRegisters)
                #print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        return IRLines


    def simplifyMoves(self, IRLines):
        simpIRLines = []
        lastWasMove = False
        linenum = 0 
        lastlinesplit = []
        for line in IRLines:
            splitline = line.line.split(" ")
            lineIsMove = "STOREI" in splitline[0] or "STOREF" in splitline[0]
            if lastWasMove and lineIsMove and splitline[-3].startswith("$") and lastlinesplit[-2] == splitline[-3]:
                simpIRLines[-1].removeTemp(splitline[-3], splitline[-2])
                #simpIRLines.append(line)
            else:
                simpIRLines.append(line)
                simpIRLines[-1].linenum = linenum
                linenum += 1

            lastWasMove = lineIsMove
            lastlinesplit = splitline
            #print(lastWasMove)
        return simpIRLines



    def printRegs(self):
        for i in self.Regs.keys():
            print("{0}: first: {1}, last: {2}".format(self.Regs[i].regName, self.Regs[i].firstUsed, self.Regs[i].lastUsed))


    def createNewIR(self, IRLines):
        newIR = ""
        for i in IRLines:
            newIR = newIR + i.line + "\n"

        return newIR

    def checkConstants(self, IRLines):
        def ifConstant(value):
            if value in regConstantDict.keys() and regConstantDict[value][1]:
                return True

            return False

        def invalidate(value):
            if value in regConstantDict.keys(): 
                regConstantDict[value][1] = 0

        newIRLines = []
        regConstantDict = {}
        oldLineisComp = False
        isLoop = False
        oldLabel = ""
        for IRLine in IRLines:
            newIRLines.append(IRLine)
            regArray = IRLine.Regs
            isStore = IRLine.op in ["STOREI", "STOREF"]
            isRead  = IRLine.op in ["READI", "READF"]

            if isLoop:
                if IRLine.op == "LABEL" and IRLine.line.split(" ")[1] == oldLabel:
                    isLoop = False
                continue

            if oldLineisComp and IRLine.op == "LABEL":
                isLoop = True
                oldLineisComp = False
                continue

            splitline = IRLine.line.split(" ")
            if isStore:
                if splitline[1].replace(".", "").replace("-", "").isdigit():
                    regConstantDict[splitline[2]] = [splitline[1], 1]
                    newIRLines.pop()
                elif ifConstant(splitline[1]):
                    regConstantDict[splitline[2]] = [regConstantDict[splitline[1]][0], 1]
                    newIRLines.pop()
                else:
                    invalidate(splitline[2])
                continue
            elif isRead:
                invalidate(splitline[1])



            isMath = IRLine.op in ["ADDI", "SUBI", "MULTI", "DIVI"]

            if isMath and ifConstant(splitline[1]) and ifConstant(splitline[2]):
                outVal = 0
                if IRLine.op.startswith("ADD"):
                    outVal = float(regConstantDict[splitline[1]][0]) + float(regConstantDict[splitline[2]][0]) 
                elif IRLine.op.startswith("SUB"):
                    outVal = float(regConstantDict[splitline[1]][0]) - float(regConstantDict[splitline[2]][0]) 
                elif IRLine.op.startswith("MULT"):
                    outVal = float(regConstantDict[splitline[1]][0]) * float(regConstantDict[splitline[2]][0]) 
                elif IRLine.op.startswith("DIV"):
                    outVal = float(regConstantDict[splitline[1]][0]) / float(regConstantDict[splitline[2]][0]) 


                if IRLine.op.endswith("I"):
                    outVal = int(outVal)
                    regConstantDict[splitline[3]] = [outVal, 1]

                else:
                    regConstantDict[splitline[3]] = [outVal, 1]
                newIRLines.pop()

            else:
                if ifConstant(splitline[1]):
                    IRLine.line = IRLine.line.replace(splitline[1], str(regConstantDict[splitline[1]][0]), 1)
                    if splitline[1] in IRLine.Regs:
                        IRLine.Regs.remove(splitline[1])
                    if isMath:
                        invalidate(splitline[3])

                if len(splitline) >= 3 and ifConstant(splitline[2]):
                    IRLine.line = IRLine.line.replace(splitline[2], str(regConstantDict[splitline[2]][0]), 1)
                    if splitline[2] in IRLine.Regs:
                        IRLine.Regs.remove(splitline[2])
                    if isMath:
                        invalidate(splitline[3])

            oldLineisComp = IRLine.op in ["GTI", "GTF", "LTI", "LTF", "EQI", "EQF", "NEI", "NEF", "GEI", "GEF", "LEI", "LEF"] 
            oldLabel = IRLine.line.split(' ')[3] if oldLineisComp else ""
 
        for line in newIRLines:
            #print(line.line)
            pass

        return newIRLines





class Register():

    def __init__(self, regName, firstUsed=0, lastUsed=-1):
        self.regName = regName
        self.firstUsed = firstUsed
        self.lastUsed = lastUsed


class IRLine():

    def __init__(self, line, lineNum):
        self.line = line
        self.Regs = []
        self.op = ""
        self.newLine = line
        self.assignVariables()
        self.lineNum = lineNum

    def assignVariables(self):
        opSplit = self.line.rstrip().split(" ")
        self.op = opSplit[0]
        for i in opSplit:
            if i.startswith("$"):
                self.Regs.append(i)

    def updateLine(self, reg, newReg):
        self.line = self.line.replace(reg, newReg, 1)
        #numReg = self.Regs.count(reg)
        #for i in range(0, numReg):
        self.Regs = [x if (x != reg) else newReg for x in self.Regs]

    def removeTemp(self, reg, replacement):
        self.line = self.line.replace(reg, replacement)
        self.Regs.remove(reg)

