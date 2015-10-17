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



class Register():

    def __init__(self, regName, firstUsed=0, lastUsed=-1):
        self.regName = regName
        self.firstUsed = firstUsed
        self.lastUsed = lastUsed


class IRLine():

    def __init__(self, line, lineNum):
        self.line = line
        self.Regs = []
        self.newLine = line
        self.assignVariables()
        self.lineNum = lineNum

    def assignVariables(self):
        opSplit = self.line.rstrip().split(" ")
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

