from antlr4 import *
from LittleExprParser import LittleExprParser
from LittleExprListener import LittleExprListener
from AST import *

# This class defines a complete listener for a parse tree produced by LittleExprParser.
class TinyGenerator():

    def __init__(self, IRcode):
        self.IRcode = IRcode
        self.tinyCode = ""
        self.declCode = ""
        self.regNum = 0
        self.tempNum = 0
        self.regDict = {}
        self.declDict = {}
        self.regVals = {}

    def generate(self):
        stmtList = self.IRcode.split("\n")
        switcher = {
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
                "GT": self.gt,
                "GE": self.ge,
                "LT": self.lt,
                "LE": self.le,
                "NE": self.ne,
                "EQ": self.eq,
                "JUMP": self.jump,
                "LABEL": self.label,
                "READI": self.readi,
                "READF": self.readf,
                "WRITEI": self.writei,
                "WRITEF": self.writef,
                "WRITES": self.writes
            }
        for line in stmtList:
            #print(line)
            # Get the function from switcher dictionary
            func = switcher.get(line.split(" ")[0], self.errorFunct)
            # Execute the function
            func(line)

        if len(self.declDict) != 0:
            self.tinyCode = "var " + "\nvar ".join(self.declDict.keys()) + "\n" + self.tinyCode + "sys halt \nend"
        else:
            self.tinyCode = self.tinyCode + "sys halt \nend"
        
        return
    def registerAllocate(self, tempName):
        if not tempName in self.regDict.keys():
            self.regDict[tempName] = self.regNum
            self.regNum += 1
            return True
        return False
    def temporaryAllocate(self):
            tempName = "&{}".format(self.tempNum)
            self.tempNum += 1
            self.registerAllocate(tempName)
            return tempName

    def mathOperandSetup(self, op1, op2, result, orderMatters):
        opmrl_op1 = ""
        opmrl_op2 = ""
        reg_op2   = ""
        op1Allocated = False

        if op1.replace(".", "").replace("-", "").isdigit():
            opmrl_op1 = op1
        elif not op1.startswith("$"):
            opmrl_op1 = op1
            self.declDict[opmrl_op1] = ""
        else:
            opAllocated = self.registerAllocate(op1)
            opmrl_op1 = "r{0}".format(self.regDict[op1])

        if op2.replace(".", "").replace("-", "").isdigit():
            opmrl_op2 = op2
        elif not op2.startswith("$"):
            opmrl_op2 = op2
            self.declDict[opmrl_op2] = ""
        else:
            self.registerAllocate(op2)
            opmrl_op2 = "r{0}".format(self.regDict[op2])

        self.registerAllocate(result)
        reg_op2 = "r{0}".format(self.regDict[result])

        if result == op1:
            return opmrl_op2, reg_op2

        if result == op2:
            if not orderMatters:
                return opmrl_op1, reg_op2
            else:
                tempName = self.temporaryAllocate()
                self.tinyCode += ("move {0} r{1}\n".format(opmrl_op2, self.regDict[tempName]))
                opmrl_op2 = "r{0}".format(self.regDict[tempName])

        if reg_op2 in self.regVals.keys():
            if opmrl_op1 == self.regVals[reg_op2][0] and self.regVals[reg_op2][1] == 1:
                return opmrl_op2, reg_op2
            else:
                self.regVals[reg_op2][1] = 0

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

        if op1.replace(".", "").replace("-", "").isdigit():
            opmrl_op1 = op1
        elif not op1.startswith("$"):
            opmrl_op1 = op1
            self.declDict[opmrl_op1] = ""
        else:
            self.registerAllocate(op1)
            opmrl_op1 = "r{0}".format(self.regDict[op1])

        if not result.startswith("$"):
            opmr_op2 = result
            self.declDict[opmr_op2] = ""
        else:
            self.registerAllocate(result)
            opmr_op2 = "r{0}".format(self.regDict[result])

        self.regVals[opmrl_op1] = [opmr_op2, 1]
        code.append("move {0} {1}".format(opmrl_op1, opmr_op2)) 
        self.tinyCode += "\n".join(code) + "\n"
        pass

    def gt(self, IRLine):
        lineSplit = IRLine.split(" ")
        op1 = lineSplit[1]
        op2 = lineSplit[2]
        result = lineSplit[3]
        pass

    def ge(self, IRLine):
        lineSplit = IRLine.split(" ")
        op1 = lineSplit[1]
        op2 = lineSplit[2]
        result = lineSplit[3]
        pass

    def lt(self, IRLine):
        lineSplit = IRLine.split(" ")
        op1 = lineSplit[1]
        op2 = lineSplit[2]
        result = lineSplit[3]
        pass

    def le(self, IRLine):
        lineSplit = IRLine.split(" ")
        op1 = lineSplit[1]
        op2 = lineSplit[2]
        result = lineSplit[3]
        pass

    def ne(self, IRLine):
        lineSplit = IRLine.split(" ")
        op1 = lineSplit[1]
        op2 = lineSplit[2]
        result = lineSplit[3]
        pass

    def eq(self, IRLine):
        lineSplit = IRLine.split(" ")
        op1 = lineSplit[1]
        op2 = lineSplit[2]
        result = lineSplit[3]
        pass

    def jump(self, IRLine):
        lineSplit = IRLine.split(" ")
        label = lineSplit[3]
        pass

    def label(self, IRLine):
        lineSplit = IRLine.split(" ")
        result = lineSplit[1]
        pass

    def readWriteOperandSetup(self, op2, code):
        opmr_op2 = ""
        if op2.replace(".", "").replace("-", "").isdigit():
            regVar = self.temporaryAllocate()
            code.append("move {0} r{1}".format(op2, self.regDict[regVar])) 
            opmr_op2 = "r" + str(self.regDict[regVar])    
        elif not op2.startswith("$"):
            opmr_op2 = op2
            self.declDict[opmr_op2] = ""
        else:
            self.registerAllocate(op2)
            opmr_op2 = "r{0}".format(self.regDict[op2])

        return opmr_op2

    def readi(self, IRLine):
        lineSplit = IRLine.split(" ")
        result = lineSplit[1]
        code = []

        opmr_op2 = self.readWriteOperandSetup(result, code)
        code.append("sys readi {0}".format(opmr_op2)) 
        
        self.tinyCode += "\n".join(code) + "\n"
        pass

    def readf(self, IRLine):
        lineSplit = IRLine.split(" ")
        result = lineSplit[1]
        code = []

        opmr_op2 = self.readWriteOperandSetup(result, code)
        code.append("sys readr {0}".format(opmr_op2)) 
        
        self.tinyCode += "\n".join(code) + "\n"
        pass

    def writei(self, IRLine):
        lineSplit = IRLine.split(" ")
        result = lineSplit[1]
        code = []

        opmr_op2 = self.readWriteOperandSetup(result, code)
        code.append("sys writei {0}".format(opmr_op2)) 
        
        self.tinyCode += "\n".join(code) + "\n"
        pass

    def writef(self, IRLine):
        lineSplit = IRLine.split(" ")
        result = lineSplit[1]
        code = []

        opmr_op2 = self.readWriteOperandSetup(result, code)
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

    def errorFunct(self, IRLine):
        pass