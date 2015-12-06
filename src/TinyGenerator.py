from antlr4 import *
from LittleExprParser import LittleExprParser
from LittleExprListener import LittleExprListener
from AST import *
from CFG import *
import re

#TODO: account for function name label1
class TinyGenerator():

    def __init__(self, IRcode, globalVariables=None, stringInit=0):
        self.IRcode = IRcode
        self.tinyCode = ""
        self.declCode = ""
        self.regNum = 0
        self.tempNum = 0
        self.regDict = {}
        self.declDict = {}
        # self.regVals = {}
        self.stringDict = {}
        # self.writeVals = {}
        self.parameters = 0
        self.functCFG = None
        self.lineNum = 0
        self.totalLineNum = 0
        self.numLocalParams = 0
        self.numTempParams = 0
        self.tempsSpilledDict = {} # Saves mapping of temp to stack in case of spilling
        self.stringInit = stringInit # If this code generation is just for the string initialization
        self.globalVariables = globalVariables
        self.stackOffset = 6
        self.registersToPush = ["r0", "r1", "r2", "r3"]

        # Add 4 registers
        self.Registers = []
        self.Registers.append(RegisterStatus(0))
        self.Registers.append(RegisterStatus(1))
        self.Registers.append(RegisterStatus(2))
        self.Registers.append(RegisterStatus(3))

        if not stringInit:
            self.functCFG = CFG(IRcode)
            self.functCFG.populateNodeInfo()
            self.functCFG.removeLinesWithNoPredecessors()
            self.functCFG.runLivenessAnalysis(globalVariables)
            self.functCFG.setLeaders()
            self.functCFG.printGraphWithNodeLists()

            # self.functCFG.printGraph()
            self.IRcode = self.functCFG.getCode()

    def generate(self):
        return self.generateCode()

    def generateCode(self):
        stmtList = self.IRcode.split("\n")
        switcher = {
                "INCI": self.inci,
                "DECI": self.deci,
                "ADDI": self.addi,
                "ADDF": self.addf,
                "SUBI": self.subi,
                "SUBF": self.subf,
                "MULTI": self.multi,
                "MULTF": self.multf,
                "DIVI": self.divi,
                "DIVF": self.divf,
                "STOREI": self.storei,
                "STOREF": self.storei,
                "STORES": self.stores,
                "GTI": self.comp,
                "GEI": self.comp,
                "LTI": self.comp,
                "LEI": self.comp,
                "NEI": self.comp,
                "EQI": self.comp,
                "GTF": self.comp,
                "GEF": self.comp,
                "LTF": self.comp,
                "LEF": self.comp,
                "NEF": self.comp,
                "EQF": self.comp,
                "JUMP": self.jump,
                "LABEL": self.label,
                "READI": self.readi,
                "READF": self.readf,
                "WRITEI": self.writei,
                "WRITEF": self.writef,
                "WRITES": self.writes,
                "JSR":self.jsr,
                "PUSH":self.push,
                "POP":self.pop,
                "RET":self.ret,
                "LINK":self.link
            }
        #set up a main caller
        code = []
        self.totalLineNum = len(stmtList)
        
        # code.append("push")
        # code.append("push r0")
        # code.append("push r1")
        # code.append("push r2")
        # code.append("push r3")

        # code.append("jsr main")

        # code.append("sys halt")

        # self.tinyCode += "\n".join(code) + "\n"

        for line in stmtList:
            #print(line)
            if not self.stringInit:
                if self.lineNum in self.functCFG.leaders:
                    self.resetRegisters(keepValid=1)
            # Get the function from switcher dictionary
            func = switcher.get(line.split(" ")[0], self.errorFunct)
            # Execute the function
            print(";", line)
            func(line)
            if not self.stringInit:
                if self.lineNum in self.functCFG.leaders:
                    self.invalidateAllRegisters()
            self.lineNum += 1
            self.printRegs()
        # print(self.regVals)

        # if len(self.declDict) != 0:
        #     self.tinyCode = "var " + "\nvar ".join(self.declDict.keys()) + "\n" + self.tinyCode + "\nend"
        # else:
        #     self.tinyCode = self.tinyCode + "\nend"
        
        self.tinyCode = re.sub(r'link.*\n', "link {0}\n".format(str(self.numLocalParams + self.numTempParams)), self.tinyCode)
        self.removeUnnecessaryMoves()
        return self.tinyCode

    def updateStackOffset(self):
        registersUsed = []
        for register in self.Registers:
            print("; Register used at least Once for {0}: {1}".format(register.regNum, str(register.usedAtLeastOnce)))
            if register.usedAtLeastOnce:
                registersUsed.append("r{0}".format(register.regNum))
        self.stackOffset = 2 + len(registersUsed)
        self.registersToPush = registersUsed


    # def countRegsUsed(self):
    #     tinyCodeArray = self.tinyCode.split("\n")
    #     regsUsed = []
    #     for tinyLine in tinyCodeArray:
    #         tinyLineSplit = tinyLine.split()
    #         if tinyLineSplit

    def resetRegisters(self, keepValid=0):
        print("; resetting reg allocation")
        registersFreed = []
        for regNum in range(4):
            if self.Registers[regNum].valid:
                self.freeRegister("r{0}".format(regNum), keepTemporaries=1)
                registersFreed.append("r{0}".format(regNum))
                if keepValid:
                    self.Registers[regNum].valid = 1
        return registersFreed

    def invalidateAllRegisters(self):
        for regNum in range(4):
            self.Registers[regNum].valid = 0

    def saveGlobalVariablesBack(self):
        print("; storing globalVariables back")
        for regNum in range(4):
            if self.Registers[regNum].valid and self.Registers[regNum].variable in self.globalVariables:
                self.freeRegister("r{0}".format(regNum))


    def removeUnnecessaryMoves(self):
        # print(self.tinyCode)
        tinyCodeArray = self.tinyCode.strip().rstrip('\n').split('\n')
        linesToRemove = []
        for tinyLine in tinyCodeArray:
            tinyLine = tinyLine.strip()
            if tinyLine == "":
                continue
            tinyLineSplit = tinyLine.split()
            if tinyLineSplit[0] != "move":
                continue
            if tinyLineSplit[1] == tinyLineSplit[2]:
                linesToRemove.append(tinyLine)

        for lineToRemove in linesToRemove:
            tinyCodeArray.remove(lineToRemove)

        self.tinyCode = "\n".join(tinyCodeArray) + "\n"
        return


    def printRegs(self):
        strToPrint = ""
        for register in self.Registers:
            strToPrint += " r{0} -> ".format(register.regNum)    
            if register.valid:
                strToPrint += register.variable
            else:
                strToPrint += "null"
        print(";", strToPrint)

        return


    def convertIRVarToTinyVar(self, IRVar):
        tinyVar = ""
        if not IRVar.startswith("$"):
            tinyVar = IRVar
            self.declDict[tinyVar] = ""
        elif IRVar.startswith("$L"):
            tinyVar = IRVar.replace("L", "-")
        elif IRVar.startswith("$P"):
            tinyVar = "$" + str(-int(IRVar[2:]) + self.stackOffset + self.parameters)
        elif IRVar.startswith("$R"):
            tinyVar = "$" + str(self.stackOffset + self.parameters)

        return tinyVar

    def ensureRegister(self, variable, doneWithLine=0):
        print("; ensuring {0}".format(variable))
        for register in self.Registers:
            if register.variable == variable and register.valid:
                return "r{0}".format(register.regNum)

        register = self.registerAllocate(variable, doneWithLine)
        tinyVar = self.convertIRVarToTinyVar(variable)
        if variable in self.tempsSpilledDict.keys():
            tinyVar = self.tempsSpilledDict[variable]
            del self.tempsSpilledDict[variable]
        self.tinyCode += "move {0} {1}\n".format(tinyVar, register)
        return register

    def checkVariableLive(self, variable):
        return variable in self.functCFG.CFGNodeList[self.lineNum].outList


    def spillRegister(self, register, keepTemporaries=0):
        regNum = int(register[1])
        tinyVar = self.convertIRVarToTinyVar(self.Registers[regNum].variable)

        if self.Registers[regNum].variable.startswith("$T") and keepTemporaries:
            return

        if self.Registers[regNum].variable.startswith("$T"):  
            tempStackVar = self.numLocalParams + 1
            while True:
                if "$-{0}".format(tempStackVar) in self.tempsSpilledDict.keys():
                    tempStackVar += 1
                    continue

                if (tempStackVar - self.numLocalParams) > self.numTempParams:
                    self.numTempParams = (tempStackVar - self.numLocalParams)

                tinyVar = "$-{0}".format(tempStackVar)
                self.tempsSpilledDict[self.Registers[regNum].variable] = tinyVar
                print("; spilling temp ",self.Registers[regNum].variable)
                break

        print("; spilling {0} to {1}".format(register, tinyVar))
        self.tinyCode += "move {0} {1}\n".format(register, tinyVar)
        return


    def freeRegister(self, register, keepTemporaries=0):
        regNum = int(register[1])
        print("; freeing {0} with {1}, valid: {2}, dirty: {3}".format(register, self.Registers[regNum].variable, self.Registers[regNum].valid, self.Registers[regNum].dirty))
        if self.Registers[regNum].valid and self.Registers[regNum].dirty and self.checkVariableLive(self.Registers[regNum].variable):
            self.spillRegister(register, keepTemporaries=keepTemporaries)
        if self.Registers[regNum].variable.startswith("$T") and keepTemporaries:  
            return
        self.Registers[regNum].valid = 0
        self.Registers[regNum].dirty = 0
        return
    

    def chooseRegToFree(self, doneWithLine=0):
        regsToUse = [0,1,2,3]
        regsToRemove = []
        if not doneWithLine:
            for regNum in regsToUse:
                if self.Registers[regNum].valid and self.Registers[regNum].variable in self.functCFG.CFGNodeList[self.lineNum].genList:
                    regsToRemove.append(regNum)
            for regNum in regsToRemove:
                regsToUse.remove(regNum)

            if len(regsToUse) == 1:
                return regsToUse[0]

            # if len(regsToUse) == 0:
            #     regsToUse = [0,1,2,3]
            #     for regNum in regsToRemove:
            #         regsToUse.remove(regNum)

        tempRegsToRemove = []
        for regNum in regsToUse:
            if self.Registers[regNum].dirty:
                tempRegsToRemove.append(regNum)

        for regNum in tempRegsToRemove:
            regsToUse.remove(regNum)

        if len(regsToUse) == 1:
            return regsToUse[0]

        if len(regsToUse) == 0:
            regsToUse = [0,1,2,3]
            for regNum in regsToRemove:
                regsToUse.remove(regNum)


        lineToCheck = self.lineNum + 1
        while True:
            print(";", regsToUse)
            if lineToCheck == (self.totalLineNum - 1):
                return regsToUse[0]
            if lineToCheck in self.functCFG.leaders:
                return regsToUse[0]

            regsToRemove = []
            for regNum in regsToUse:
                if self.Registers[regNum].variable in self.functCFG.CFGNodeList[lineToCheck].genList:
                    regsToRemove.append(regNum)

            for regNum in regsToRemove:
                regsToUse.remove(regNum)
                if len(regsToUse) == 1:
                    return regsToUse[0]
            lineToCheck += 1

    def chooseAndFreeRegister(self, doneWithLine=0):
        regNum = self.chooseRegToFree(doneWithLine)
        self.freeRegister("r{0}".format(regNum))
        return regNum

    def registerAllocate(self, varName, doneWithLine=0, registersToUse=[]):
        print("; starting allocation of {0}".format(varName))
        regNum = 0
        if len(registersToUse) != 0:
            regNum = int(registersToUse[0][1])
        else:
            for register in self.Registers:
                if not register.valid: 
                    register.valid = 1
                    register.dirty = 0
                    register.variable = varName
                    print("; allocating {0} to r{1}".format(varName, register.regNum))
                    register.usedAtLeastOnce = True
                    return "r{0}".format(register.regNum)
                    # foundReg = 1
                    # regToUse = register.regNum

            regNum = self.chooseAndFreeRegister(doneWithLine)

        self.Registers[regNum].valid = 1
        self.Registers[regNum].dirty = 0
        self.Registers[regNum].variable = varName
        self.Registers[regNum].usedAtLeastOnce = True
        print("; allocating {0} to r{1}".format(varName, regNum))
        return "r{0}".format(regNum)

    def freeRegistersIfDead(self, variablesToTryFree, keepVariablesLive=[]):
        registersFreed = []
        for regNum in range(4):
            if self.Registers[regNum].valid and self.Registers[regNum].variable in variablesToTryFree and self.Registers[regNum].variable not in keepVariablesLive:
                if (not self.checkVariableLive(self.Registers[regNum].variable)) or (self.Registers[regNum].variable in self.functCFG.CFGNodeList[self.lineNum].killList):
                    print("; freeing cause dead r{0} with {1} -> {2}".format(regNum, self.Registers[regNum].variable, self.functCFG.CFGNodeList[self.lineNum].outList))
                    self.Registers[regNum].valid = 0
                    self.Registers[regNum].dirty = 0
                    registersFreed.append("r{0}".format(regNum))

        return registersFreed


    def temporaryAllocate(self):
            tempName = "&{}".format(self.tempNum)
            self.functCFG.CFGNodeList[self.lineNum].genList.append(tempName)
            self.tempNum += 1
            return self.registerAllocate(tempName)

    def incDecOperandSetup(self, op1):
        opmrl_op1 = ""
        opmrl_op2 = ""
        reg_op2   = ""
        isReg1    = False
        op1Allocated = False

        # if op1.replace(".", "").replace("-", "").isdigit():
        #     opmrl_op1 = op1
        # elif not op1.startswith("$"):
        #     opmrl_op1 = op1
        #     self.declDict[opmrl_op1] = ""
        # elif op1.startswith("$L"):
        #     opmrl_op1 = op1.replace("L", "-")
        # elif op1.startswith("$P"):
        #     opmrl_op1 = "$" + str(-int(op1[2:]) + 6 + self.parameters)
        # elif op1.startswith("$R"):
        #     opmrl_op1 = "$" + str(6 + self.parameters)
        # else:
            # opAllocated = self.registerAllocate(op1)
            # opmrl_op1 = "r{0}".format(self.regDict[op1])
        reg_op2 = self.ensureRegister(op1, 0)
        self.markRegisterDirty(reg_op2)

        # self.registerAllocate(op1)
        # reg_op2 = "r{0}".format(self.regDict[op1])

        # if opmrl_op1 in self.writeVals.keys():
        #     reg_op2 = "r{0}".format(self.writeVals[opmrl_op1])
        #     self.regDict[result] = self.writeVals[opmrl_op1]
        #     self.writeVals.pop(opmrl_op1)
        # else:
        # self.tinyCode += ("move {0} {1}\n".format(opmrl_op1, reg_op2))
        return reg_op2

    def inci(self, IRLine):
        lineSplit = IRLine.split(" ")
        op1 = lineSplit[1]
        code = []

        reg_op2 = self.incDecOperandSetup(op1)
        code.append("inci {0}".format(reg_op2))

        self.tinyCode += "\n".join(code) + "\n"

        regsToTryFree = []
        regsToTryFree.append(op1)

        self.freeRegistersIfDead(regsToTryFree)
        return

    def deci(self, IRLine):
        lineSplit = IRLine.split(" ")
        op1 = lineSplit[1]
        code = []

        reg_op2 = self.incDecOperandSetup(op1)
        code.append("deci {0}".format(reg_op2))

        self.tinyCode += "\n".join(code) + "\n"

        regsToTryFree = []
        regsToTryFree.append(op1)

        self.freeRegistersIfDead(regsToTryFree)
        return

    def mathOperandSetup(self, op1, op2, result, orderMatters):
        opmrl_op1 = ""
        opmrl_op2 = ""
        reg_op2   = ""
        op1Allocated = False
        isReg1 = False
        isReg2 = False

        if op1.replace(".", "").replace("-", "").isdigit():
            opmrl_op1 = op1
        # elif not op1.startswith("$"):
        #     opmrl_op1 = op1
        #     self.declDict[opmrl_op1] = ""
        # elif op1.startswith("$L"):
        #     opmrl_op1 = op1.replace("L", "-")
        # elif op1.startswith("$P"):
        #     opmrl_op1 = "$" + str(-int(op1[2:]) + 6 + self.parameters)
        # elif op1.startswith("$R"):
        #     opmrl_op1 = "$" + str(6 + self.parameters)
        else:
            opmrl_op1 = self.ensureRegister(op1, 0)
            isReg1 = True
            # opAllocated = self.registerAllocate(op1)
            # opmrl_op1 = "r{0}".format(self.regDict[op1])

        if op2.replace(".", "").replace("-", "").isdigit():
            opmrl_op2 = op2
        # elif not op2.startswith("$"):
        #     opmrl_op2 = op2
        #     self.declDict[opmrl_op2] = ""
        # elif op2.startswith("$L"):
        #     opmrl_op2 = op2.replace("L", "-")
        # elif op2.startswith("$P"):
        #     opmrl_op2 = "$" + str(-int(op2[2:]) + 6 + self.parameters)
        # elif op2.startswith("$R"):
        #     opmrl_op2 = "$" + str(6 + self.parameters)
        else:
            opmrl_op2 = self.ensureRegister(op2, 0)
            isReg2 = True
            # self.registerAllocate(op2)
            # opmrl_op2 = "r{0}".format(self.regDict[op2])

        regsToTryFree = []
        if isReg1:
            regsToTryFree.append(op1)
        if isReg2:
            regsToTryFree.append(op2)

        registersFreed = self.freeRegistersIfDead(regsToTryFree, keepVariablesLive=[op2])
        reg_op2 = self.registerAllocate(result, doneWithLine=0, registersToUse=registersFreed)
        self.markRegisterDirty(reg_op2)
        self.freeRegistersIfDead(regsToTryFree)
        # self.registerAllocate(result)
        # reg_op2 = "r{0}".format(self.regDict[result])

        # if result == op1:
        #     return opmrl_op2, reg_op2

        # if result == op2:
            # if not orderMatters:
            #     return opmrl_op1, reg_op2
            # else:
            #     tempName = self.temporaryAllocate()
            #     # if opmrl_op1 in self.writeVals.keys():
            #     #     opmrl_op2 = "r{0}".format(self.writeVals[opmrl_op1])
            #     # else:
            #     self.tinyCode += ("move {0} r{1}\n".format(opmrl_op2, self.regDict[tempName]))
            #     opmrl_op2 = "r{0}".format(self.regDict[tempName])

        # print("{0}: {1}".format(result, reg_op2))
        # print(" :::: ".join([op1, op2, result, str(orderMatters)]))
        # if reg_op2 in self.regVals.keys():
        #     # print(reg_op2)
        #     # print(self.regVals)
        #     if opmrl_op1 == self.regVals[reg_op2][0] and self.regVals[reg_op2][1] == 1:
        #         return opmrl_op2, reg_op2
        #     else:
        #         self.regVals[reg_op2][1] = 0

        # if opmrl_op1 in self.writeVals.keys():
        #     reg_op2 = "r{0}".format(self.writeVals[opmrl_op1])
        #     self.regDict[result] = self.writeVals[opmrl_op1]
        #     self.writeVals.pop(opmrl_op1)
        # else:
        print("; opmrl_op1 = {0}, opmrl_op2 = {1}, reg_op2 = {2}".format(opmrl_op1, opmrl_op2, reg_op2))
        self.tinyCode += ("move {0} {1}\n".format(opmrl_op1, reg_op2))
        return opmrl_op2, reg_op2

    def addi(self, IRLine):
        lineSplit = IRLine.split(" ")
        op1 = lineSplit[1]
        op2 = lineSplit[2]
        result = lineSplit[3]
        code = []

        opmrl_op1, reg_op2 = self.mathOperandSetup(op1, op2, result, False)
        code.append("addi {0} {1}".format(opmrl_op1, reg_op2))

        self.tinyCode += "\n".join(code) + "\n"
        pass

    def addf(self, IRLine):
        lineSplit = IRLine.split(" ")
        op1 = lineSplit[1]
        op2 = lineSplit[2]
        result = lineSplit[3]
        code = []

        opmrl_op1, reg_op2 = self.mathOperandSetup(op1, op2, result, False) 
        code.append("addr {0} {1}".format(opmrl_op1, reg_op2))

        self.tinyCode += "\n".join(code) + "\n"
        pass

    def subi(self, IRLine):
        lineSplit = IRLine.split(" ")
        op1 = lineSplit[1]
        op2 = lineSplit[2]
        result = lineSplit[3]
        code = []

        opmrl_op1, reg_op2 = self.mathOperandSetup(op1, op2, result, True) 
        code.append("subi {0} {1}".format(opmrl_op1, reg_op2))
        
        self.tinyCode += "\n".join(code) + "\n"
        pass

    def subf(self, IRLine):
        lineSplit = IRLine.split(" ")
        op1 = lineSplit[1]
        op2 = lineSplit[2]
        result = lineSplit[3]
        code = []

        opmrl_op1, reg_op2 = self.mathOperandSetup(op1, op2, result, True) 
        code.append("subr {0} {1}".format(opmrl_op1, reg_op2))
        
        self.tinyCode += "\n".join(code) + "\n"
        pass

    def multi(self, IRLine):
        lineSplit = IRLine.split(" ")
        op1 = lineSplit[1]
        op2 = lineSplit[2]
        result = lineSplit[3]
        code = []

        opmrl_op1, reg_op2 = self.mathOperandSetup(op1, op2, result, False) 
        code.append("muli {0} {1}".format(opmrl_op1, reg_op2))
        
        self.tinyCode += "\n".join(code) + "\n"
        pass

    def multf(self, IRLine):
        lineSplit = IRLine.split(" ")
        op1 = lineSplit[1]
        op2 = lineSplit[2]
        result = lineSplit[3]
        code = []

        opmrl_op1, reg_op2 = self.mathOperandSetup(op1, op2, result, False) 
        code.append("mulr {0} {1}".format(opmrl_op1, reg_op2))
        
        self.tinyCode += "\n".join(code) + "\n"
        pass

    def divi(self, IRLine):
        lineSplit = IRLine.split(" ")
        op1 = lineSplit[1]
        op2 = lineSplit[2]
        result = lineSplit[3]
        code = []

        opmrl_op1, reg_op2 = self.mathOperandSetup(op1, op2, result, True) 
        code.append("divi {0} {1}".format(opmrl_op1, reg_op2))
        
        self.tinyCode += "\n".join(code) + "\n"
        pass

    def divf(self, IRLine):
        lineSplit = IRLine.split(" ")
        op1 = lineSplit[1]
        op2 = lineSplit[2]
        result = lineSplit[3]
        code = []

        opmrl_op1, reg_op2 = self.mathOperandSetup(op1, op2, result, True) 
        code.append("divr {0} {1}".format(opmrl_op1, reg_op2))
        
        self.tinyCode += "\n".join(code) + "\n"
        pass

    def storei(self, IRLine):
        lineSplit = IRLine.split(" ")
        op1 = lineSplit[1]
        result = lineSplit[2]
        code  = []
        opmrl_op1 = ""
        opmr_op2  = ""
        isMem1 = False
        isMem2 = False
        isReg1 = False

        if op1.replace(".", "").replace("-", "").isdigit():
            opmrl_op1 = op1
        # elif not op1.startswith("$"):
        #     isMem1 = True
        #     opmrl_op1 = op1
        #     self.declDict[opmrl_op1] = ""
        # elif op1.startswith("$L"):
        #     isMem1 = True
        #     opmrl_op1 = op1.replace("L", "-")
        # elif op1.startswith("$P"):
        #     isMem1 = True
        #     opmrl_op1 = "$" + str(-int(op1[2:]) + 6 + self.parameters)
        # elif op1.startswith("$R"):
        #     isMem1 = True
        #     opmrl_op1 = "$" + str(6 + self.parameters)
        else:
            opmrl_op1 = self.ensureRegister(op1, 0)
            isReg1 = True

        #     opmrl_op2 = self.ensureRegister(op2, 0)
        #     isReg2 = True
        #     # self.registerAllocate(op2)
        #     # opmrl_op2 = "r{0}".format(self.regDict[op2])

        regsToTryFree = []
        if isReg1:
            regsToTryFree.append(op1)
        # if isReg2:
        #     regsToTryFree.append(opmrl_op2)

        # reg_op2 = self.registerAllocate(result, 1)
        # self.Registers[int(reg_op2[1])].dirty = 1

        # if not result.startswith("$"):
        #     isMem2 = True
        #     opmr_op2 = result
        #     self.declDict[opmr_op2] = ""
        # elif result.startswith("$L"):
        #     isMem2 = True
        #     opmr_op2 = result.replace("L", "-")
        # elif result.startswith("$P"):
        #     isMem2 = True
        #     opmr_op2 = "$" + str(-int(result[2:]) + 6 + self.parameters)
        # elif result.startswith("$R"):
        #     isMem2 = True
        #     opmr_op2 = "$" + str(6 + self.parameters)
        # else:
            # self.registerAllocate(result)
            # opmr_op2 = "r{0}".format(self.regDict[result])
        registersFreed = self.freeRegistersIfDead(regsToTryFree)
        if result.startswith("$R"):
            isMem2 = True
            opmr_op2 = "$" + str(self.stackOffset + self.parameters)
        else:
            opmr_op2 = self.registerAllocate(result, 1, registersToUse=registersFreed)
            # self.Registers[int(opmr_op2[1])].dirty = 1
            self.markRegisterDirty(opmr_op2)

        # print("{0}: {1}".format(opmrl_op1, opmr_op2))
        # print(IRLine)
        # self.regVals[opmr_op2 ] = [opmrl_op1, 1]

        # if isMem1 and isMem2:
        #     tempName = self.temporaryAllocate()
        #     code.append("move {0} r{1}".format(opmrl_op1, self.regDict[tempName])) 
        #     opmrl_op1 = "r{0}".format(self.regDict[tempName])

        print("; move {0} {1}".format(opmrl_op1, opmr_op2))
        code.append("move {0} {1}".format(opmrl_op1, opmr_op2)) 
        self.tinyCode += "\n".join(code) + "\n"
        return

    def stores(self, IRLine):
        lineSplit = IRLine.split(" ")
        # op1 = lineSplit[1]
        result = " ".join(lineSplit[1:-1])
        op1 = lineSplit[-1]
        code  = []

        # code.append("str {0} {1}".format(op1, result))
        if op1.startswith("$L"):
            # self.tinyCode += "\n".join(code) + "\n"
            self.tinyCode += "str {0} {1}\n".format(op1, result)
        else:
            self.tinyCode = "str {0} {1}\n".format(op1, result) + self.tinyCode
            # self.tinyCode = "\n".join(code) + "\n" + self.tinyCode

        return

    def compOperand(self, op1, op2, dataType):
        code = []
        opmrl_op1 = ""
        opmrl_op2 = ""
        reg_op2   = ""
        op1Allocated = False
        flipped = False
        isReg1 = False
        isReg2 = False

        if (not op1.replace(".", "").replace("-", "").isdigit()) and (op2.replace(".", "").replace("-", "").isdigit()):
            flipped = True
            op2, op1 = op1, op2

        if op1.replace(".", "").replace("-", "").isdigit():
            opmrl_op1 = op1
        # elif not op1.startswith("$"):
        #     opmrl_op1 = op1
        #     self.declDict[opmrl_op1] = ""
        # elif op1.startswith("$L"):
        #     opmrl_op1 = op1.replace("L", "-")
        # elif op1.startswith("$P"):
        #     opmrl_op1 = "$" + str(-int(op1[2:]) + 6 + self.parameters)
        # elif op1.startswith("$R"):
        #     opmrl_op1 = "$" + str(6 + self.parameters)
        else:
            # opAllocated = self.registerAllocate(op1)
            # opmrl_op1 = "r{0}".format(self.regDict[op1])
            opmrl_op1 = self.ensureRegister(op1, 0)
            isReg1 = True

        if op2.replace(".", "").replace("-", "").isdigit():
            # opmrl_op2 = op2
            opmr_op2 = self.temporaryAllocate()
        # elif not op2.startswith("$"):
        #     opmrl_op2 = op2
        #     self.declDict[opmrl_op2] = ""
        # elif op2.startswith("$L"):
        #     opmrl_op2 = op2.replace("L", "-")
        # elif op2.startswith("$P"):
        #     opmrl_op2 = "$" + str(-int(op2[2:]) + 6 + self.parameters)
        # elif op2.startswith("$R"):
        #     opmrl_op2 = "$" + str(6 + self.parameters)
        else:
            opmrl_op2 = self.ensureRegister(op2, 0)
            # self.registerAllocate(op2)
            # opmrl_op2 = "r{0}".format(self.regDict[op2])
            isReg2 = True

        regsToTryFree = []
        if isReg1:
            regsToTryFree.append(op1)
        if isReg2:
            regsToTryFree.append(op2)

        self.freeRegistersIfDead(regsToTryFree)

        # if isReg1 and not isReg2:
        #     temp = opmrl_op2
        #     opmrl_op2 = opmrl_op1
        #     opmrl_op1 = temp
        #     flipped = True
        # elif not isReg2:
        #     opmrl_op2 = self.temporaryAllocate()
        #     if op2.startswith("$L"):
        #         op2 = op2.replace("L", "-")
        #     elif op2.startswith("$P"):
        #         op2 = "$" + str(-int(op2[2:]) + 6 + self.parameters)
        #     elif op2.startswith("$R"):
        #         op2 = "$" + str(6 + self.parameters)

        #     code.append("move {0} r{1}".format(op2, self.regDict[opmrl_op2]))
        #     opmrl_op2 = "r{0}".format(self.regDict[opmrl_op2])  

        if dataType:
            code.append("cmpi {0} {1}".format(opmrl_op1, opmrl_op2))
        else:
            code.append("cmpr {0} {1}".format(opmrl_op1, opmrl_op2))
    

        self.tinyCode += "\n".join(code) + "\n"
        return flipped

    def comp(self, IRLine):
        lineSplit = IRLine.split(" ")
        op  = lineSplit[0]
        op1 = lineSplit[1]
        op2 = lineSplit[2]
        label = lineSplit[3]
        CompOP = None
        code = []

        if op in ["LTI", "LTF"]:
            CompOP = COMPOP.LT
        elif op in ["GTI","GTF"]:
            CompOP = COMPOP.GT
        elif op in ["EQI","EQF"]:
            CompOP = COMPOP.EQ
        elif op in ["NEI","NEF"]:
            CompOP = COMPOP.NE
        elif op in ["LEI","LEF"]:
            CompOP = COMPOP.LE
        elif op in ["GEI","GEF"]:
            CompOP = COMPOP.GE

        flipped = self.compOperand(op1, op2, op.endswith("I"))
        if flipped:
            CompOP = COMPOP.inverseTinyOP(CompOP)

        if CompOP == COMPOP.LT:
            code.append("jlt {0}".format(label))
        elif CompOP == COMPOP.GT:
            code.append("jgt {0}".format(label))
        elif CompOP == COMPOP.EQ:
            code.append("jeq {0}".format(label))
        elif CompOP == COMPOP.NE:
            code.append("jne {0}".format(label))
        elif CompOP == COMPOP.LE:
            code.append("jle {0}".format(label))
        elif CompOP == COMPOP.GE:
            code.append("jge {0}".format(label))

        self.tinyCode += "\n".join(code) + "\n"
        return

    def jump(self, IRLine):
        lineSplit = IRLine.split(" ")
        label = lineSplit[1]
        code = []

        code.append("jmp {0}".format(label))    
        self.tinyCode += "\n".join(code) + "\n"

        return

    def label(self, IRLine):
        lineSplit = IRLine.split(" ")
        label = lineSplit[1]
        code = []

        code.append("label {0}".format(label))    
        self.tinyCode += "\n".join(code) + "\n"

        return

    def readWriteOperandSetup(self, op2, code):
        opmr_op2 = ""
        if op2.replace(".", "").replace("-", "").isdigit():
            # if op2 in self.writeVals.keys():
            #     opmr_op2 = "r" + str(self.writeVals[op2])
            # else:
            regVar = self.temporaryAllocate()
            code.append("move {0} r{1}".format(op2, self.regDict[regVar])) 
            opmr_op2 = "r" + str(self.regDict[regVar])   
                # self.writeVals[op2] = self.regDict[regVar] 
        elif not op2.startswith("$"):
            opmr_op2 = op2
            self.declDict[opmr_op2] = ""
        elif op2.startswith("$L"):
            opmr_op2 = op2.replace("L", "-")
        elif op2.startswith("$P"):
            opmr_op2 = "$" + str(-int(op2[2:]) + self.stackOffset + self.parameters)
        elif op2.startswith("$R"):
            opmr_op2 = "$" + str(self.stackOffset + self.parameters)
        else:
            self.registerAllocate(op2)
            opmr_op2 = "r{0}".format(self.regDict[op2])

        return opmr_op2

    def markRegisterDirty(self, op):
        self.Registers[int(op[1])].dirty = 1
        return


    def readOperandSetup(self, op2, code):
        reg_op2 = self.registerAllocate(op2, 1)
        self.markRegisterDirty(reg_op2)
        return reg_op2
        # pass

    def writeOperandSetup(self, op2, code):
        opmr_op2 = ""
        if op2.replace(".", "").replace("-", "").isdigit():
            # if op2 in self.writeVals.keys():
            #     opmr_op2 = "r" + str(self.writeVals[op2])
            # else:
            opmr_op2 = self.temporaryAllocate()
            code.append("move {0} {1}".format(op2, opmr_op2)) 
                # self.writeVals[op2] = self.regDict[regVar] 
        # elif not op2.startswith("$"):
        #     opmr_op2 = op2
        #     self.declDict[opmr_op2] = ""
        # elif op2.startswith("$L"):
        #     opmr_op2 = op2.replace("L", "-")
        # elif op2.startswith("$P"):
        #     opmr_op2 = "$" + str(-int(op2[2:]) + 6 + self.parameters)
        # elif op2.startswith("$R"):
        #     opmr_op2 = "$" + str(6 + self.parameters)
        else:
            # self.registerAllocate(op2)
            opmr_op2 = self.ensureRegister(op2, 0)

        self.freeRegistersIfDead([op2])
        return opmr_op2


    def readi(self, IRLine):
        lineSplit = IRLine.split(" ")
        result = lineSplit[1]
        code = []

        opmr_op2 = self.readOperandSetup(result, code)
        code.append("sys readi {0}".format(opmr_op2)) 
        
        self.tinyCode += "\n".join(code) + "\n"
        pass

    def readf(self, IRLine):
        lineSplit = IRLine.split(" ")
        result = lineSplit[1]
        code = []

        opmr_op2 = self.readOperandSetup(result, code)
        code.append("sys readr {0}".format(opmr_op2)) 
        
        self.tinyCode += "\n".join(code) + "\n"
        pass

    def writei(self, IRLine):
        lineSplit = IRLine.split(" ")
        result = lineSplit[1]
        code = []

        opmr_op2 = self.writeOperandSetup(result, code)
        code.append("sys writei {0}".format(opmr_op2)) 
        
        self.tinyCode += "\n".join(code) + "\n"
        pass

    def writef(self, IRLine):
        lineSplit = IRLine.split(" ")
        result = lineSplit[1]
        code = []

        opmr_op2 = self.writeOperandSetup(result, code)
        code.append("sys writer {0}".format(opmr_op2)) 
        
        self.tinyCode += "\n".join(code) + "\n"
        pass

    def writes(self, IRLine):
        lineSplit = IRLine.split(" ")
        result = lineSplit[1]
        code = []

        code.append("sys writes {0}".format(result)) 
        
        self.tinyCode += "\n".join(code) + "\n"
        pass

    def jsr(self, IRLine):
        lineSplit = IRLine.split(" ")
        label = lineSplit[1]
        code = []
        self.saveGlobalVariablesBack()

        code.append("push r0")
        code.append("push r1")
        code.append("push r2")
        code.append("push r3")

        code.append("jsr {0}".format(label))

        code.append("pop r3")
        code.append("pop r2")
        code.append("pop r1")
        code.append("pop r0")

        self.tinyCode += "\n".join(code) + "\n"

    def push(self, IRLine):
        lineSplit = IRLine.rstrip().split(" ")
        code = []
        value = ""
        isReg1 = False
        if len(lineSplit) == 2:
            op1 = lineSplit[1]
            if op1.replace(".", "").replace("-", "").isdigit():
                value = op1
            # elif not op1.startswith("$"):
            #     value = op1         
            # elif op1.startswith("$L"):
            #     value = op1.replace("L", "-")
            # elif op1.startswith("$P"):
            #     value = "$" + str(-int(op1[2:]) + 6 + self.parameters)
            # elif op1.startswith("$R"):
            #     value = "$" + str(6 + self.parameters)
            else:
                value = self.ensureRegister(op1)
                isReg1 = True

            if isReg1:
                self.freeRegistersIfDead([op1])
                # self.registerAllocate(op1)
                # value = "r{0}".format(self.regDict[op1])
            code.append("push {0}".format(value))
        else:
            code.append("push")


        self.tinyCode += "\n".join(code) + "\n"

    def pop(self, IRLine):
        lineSplit = IRLine.rstrip().split(" ")
        code = []
        if len(lineSplit) == 2:
            op1 = lineSplit[1]
            # if not op1.startswith("$"):
            #     value = op1            
            # elif op1.startswith("$L"):
            #     value = op1.replace("L", "-")
            # elif op1.startswith("$P"):
            #     value = "$" + str(-int(op1[2:]) + 6 + self.parameters)
            # elif op1.startswith("$R"):
            #     value = "$" + str(6 + self.parameters)
            # else:
                # self.registerAllocate(op1)
                # value = "r{0}".format(self.regDict[op1])
            # if op1.startswith("$T"):
            #     value = self.temporaryAllocate()
            # else:
            value = self.registerAllocate(op1)
            code.append("pop {0}".format(value))
        else:
            code.append("pop")

        self.tinyCode += "\n".join(code) + "\n"

    def ret(self, IRLine):
        code = []
        self.saveGlobalVariablesBack()
        code.append("unlnk")
        code.append("ret")
        self.tinyCode += "\n".join(code) + "\n"

    def link(self, IRLine):
        lineSplit = IRLine.split(" ")
        parameters = lineSplit[2]
        localparam = lineSplit[1]
        code = []
        self.parameters = int(parameters)
        code.append("link {0}".format(localparam))
        self.numLocalParams = int(localparam)
        self.tinyCode += "\n".join(code) + "\n"

    def errorFunct(self, IRLine):
        pass


class RegisterStatus():
    def __init__(self, regNum):
        self.dirty = 0
        self.valid = 0
        self.variable = ""
        self.regNum = regNum
        self.usedAtLeastOnce = False
# 31 classes WOAH