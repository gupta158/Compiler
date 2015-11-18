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
        self.stringDict = {}
        self.writeVals = {}
        self.parameters = 0;

    def generate(self):
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
        
        code.append("push")
        code.append("push r0")
        code.append("push r1")
        code.append("push r2")
        code.append("push r3")

        code.append("jsr main")

        code.append("sys halt")

        self.tinyCode += "\n".join(code) + "\n"

        for line in stmtList:
            #print(line)
            # Get the function from switcher dictionary
            func = switcher.get(line.split(" ")[0], self.errorFunct)
            # Execute the function
            func(line)
        # print(self.regVals)

        if len(self.declDict) != 0:
            self.tinyCode = "var " + "\nvar ".join(self.declDict.keys()) + "\n" + self.tinyCode + "\nend"
        else:
            self.tinyCode = self.tinyCode + "\nend"
        
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

    def incDecOperandSetup(self, op1):
        opmrl_op1 = ""
        opmrl_op2 = ""
        reg_op2   = ""
        op1Allocated = False

        if op1.replace(".", "").replace("-", "").isdigit():
            opmrl_op1 = op1
        elif not op1.startswith("$"):
            opmrl_op1 = op1
            self.declDict[opmrl_op1] = ""
        elif op1.startswith("$L"):
            opmrl_op1 = op1.replace("L", "-")
        elif op1.startswith("$P"):
            opmrl_op1 = "$" + str(-int(op1[2:]) + 6 + self.parameters)
        elif op1.startswith("$R"):
            opmrl_op1 = "$" + str(6 + self.parameters)
        else:
            opAllocated = self.registerAllocate(op1)
            opmrl_op1 = "r{0}".format(self.regDict[op1])

        self.registerAllocate(op1)
        reg_op2 = "r{0}".format(self.regDict[op1])

        if opmrl_op1 in self.writeVals.keys():
            reg_op2 = "r{0}".format(self.writeVals[opmrl_op1])
            self.regDict[result] = self.writeVals[opmrl_op1]
            self.writeVals.pop(opmrl_op1)
        else:
            self.tinyCode += ("move {0} {1}\n".format(opmrl_op1, reg_op2))

        return reg_op2, opmrl_op1

    def inci(self, IRLine):
        lineSplit = IRLine.split(" ")
        op1 = lineSplit[1]
        code = []

        reg_op2, opmrl_op1 = self.incDecOperandSetup(op1)
        code.append("inci {0}".format(reg_op2))
        if not opmrl_op1.startswith("r"):
            code.append("move {0} {1}".format(reg_op2, opmrl_op1))
        self.tinyCode += "\n".join(code) + "\n"
        return

    def deci(self, IRLine):
        lineSplit = IRLine.split(" ")
        op1 = lineSplit[1]
        code = []

        reg_op2, opmrl_op1 = self.incDecOperandSetup(op1)
        code.append("deci {0}".format(reg_op2))
        if not opmrl_op1.startswith("r"):
            code.append("move {0} {1}".format(reg_op2, opmrl_op1))
        self.tinyCode += "\n".join(code) + "\n"

        return

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
        elif op1.startswith("$L"):
            opmrl_op1 = op1.replace("L", "-")
        elif op1.startswith("$P"):
            opmrl_op1 = "$" + str(-int(op1[2:]) + 6 + self.parameters)
        elif op1.startswith("$R"):
            opmrl_op1 = "$" + str(6 + self.parameters)
        else:
            opAllocated = self.registerAllocate(op1)
            opmrl_op1 = "r{0}".format(self.regDict[op1])

        if op2.replace(".", "").replace("-", "").isdigit():
            opmrl_op2 = op2
        elif not op2.startswith("$"):
            opmrl_op2 = op2
            self.declDict[opmrl_op2] = ""
        elif op2.startswith("$L"):
            opmrl_op2 = op2.replace("L", "-")
        elif op2.startswith("$P"):
            opmrl_op2 = "$" + str(-int(op2[2:]) + 6 + self.parameters)
        elif op2.startswith("$R"):
            opmrl_op2 = "$" + str(6 + self.parameters)
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
                if opmrl_op1 in self.writeVals.keys():
                    opmrl_op2 = "r{0}".format(self.writeVals[opmrl_op1])
                else:
                    self.tinyCode += ("move {0} r{1}\n".format(opmrl_op2, self.regDict[tempName]))
                    opmrl_op2 = "r{0}".format(self.regDict[tempName])

        # print("{0}: {1}".format(result, reg_op2))
        # print(" :::: ".join([op1, op2, result, str(orderMatters)]))
        if reg_op2 in self.regVals.keys():
            # print(reg_op2)
            # print(self.regVals)
            if opmrl_op1 == self.regVals[reg_op2][0] and self.regVals[reg_op2][1] == 1:
                return opmrl_op2, reg_op2
            else:
                self.regVals[reg_op2][1] = 0

        if opmrl_op1 in self.writeVals.keys():
            reg_op2 = "r{0}".format(self.writeVals[opmrl_op1])
            self.regDict[result] = self.writeVals[opmrl_op1]
            self.writeVals.pop(opmrl_op1)
        else:
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

        if op1.replace(".", "").replace("-", "").isdigit():
            opmrl_op1 = op1
        elif not op1.startswith("$"):
            isMem1 = True
            opmrl_op1 = op1
            self.declDict[opmrl_op1] = ""
        elif op1.startswith("$L"):
            isMem1 = True
            opmrl_op1 = op1.replace("L", "-")
        elif op1.startswith("$P"):
            isMem1 = True
            opmrl_op1 = "$" + str(-int(op1[2:]) + 6 + self.parameters)
        elif op1.startswith("$R"):
            isMem1 = True
            opmrl_op1 = "$" + str(6 + self.parameters)
        else:
            self.registerAllocate(op1)
            opmrl_op1 = "r{0}".format(self.regDict[op1])

        if not result.startswith("$"):
            isMem2 = True
            opmr_op2 = result
            self.declDict[opmr_op2] = ""
        elif result.startswith("$L"):
            isMem2 = True
            opmr_op2 = result.replace("L", "-")
        elif result.startswith("$P"):
            isMem2 = True
            opmr_op2 = "$" + str(-int(result[2:]) + 6 + self.parameters)
        elif result.startswith("$R"):
            isMem2 = True
            opmr_op2 = "$" + str(6 + self.parameters)
        else:
            self.registerAllocate(result)
            opmr_op2 = "r{0}".format(self.regDict[result])


        # print("{0}: {1}".format(opmrl_op1, opmr_op2))
        # print(IRLine)
        self.regVals[opmr_op2 ] = [opmrl_op1, 1]

        if isMem1 and isMem2:
            tempName = self.temporaryAllocate()
            code.append("move {0} r{1}".format(opmrl_op1, self.regDict[tempName])) 
            opmrl_op1 = "r{0}".format(self.regDict[tempName])

        code.append("move {0} {1}".format(opmrl_op1, opmr_op2)) 
        self.tinyCode += "\n".join(code) + "\n"
        return

    def stores(self, IRLine):
        lineSplit = IRLine.split(" ")
        # op1 = lineSplit[1]
        result = " ".join(lineSplit[1:-1])
        op1 = lineSplit[-1]
        code  = []

        code.append("str {0} {1}".format(op1, result))
        if op1.startswith("$L"):
            self.tinyCode += "\n".join(code) + "\n"
        else:
            self.tinyCode = "\n".join(code) + "\n" + self.tinyCode
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

        if op1.replace(".", "").replace("-", "").isdigit():
            opmrl_op1 = op1
        elif not op1.startswith("$"):
            opmrl_op1 = op1
            self.declDict[opmrl_op1] = ""
        elif op1.startswith("$L"):
            opmrl_op1 = op1.replace("L", "-")
        elif op1.startswith("$P"):
            opmrl_op1 = "$" + str(-int(op1[2:]) + 6 + self.parameters)
        elif op1.startswith("$R"):
            opmrl_op1 = "$" + str(6 + self.parameters)
        else:
            opAllocated = self.registerAllocate(op1)
            opmrl_op1 = "r{0}".format(self.regDict[op1])
            isReg1 = True

        if op2.replace(".", "").replace("-", "").isdigit():
            opmrl_op2 = op2
        elif not op2.startswith("$"):
            opmrl_op2 = op2
            self.declDict[opmrl_op2] = ""
        elif op2.startswith("$L"):
            opmrl_op2 = op2.replace("L", "-")
        elif op2.startswith("$P"):
            opmrl_op2 = "$" + str(-int(op2[2:]) + 6 + self.parameters)
        elif op2.startswith("$R"):
            opmrl_op2 = "$" + str(6 + self.parameters)
        else:
            self.registerAllocate(op2)
            opmrl_op2 = "r{0}".format(self.regDict[op2])
            isReg2 = True

        if isReg1 and not isReg2:
            temp = opmrl_op2
            opmrl_op2 = opmrl_op1
            opmrl_op1 = temp
            flipped = True
        elif not isReg2:
            opmrl_op2 = self.temporaryAllocate()
            if op2.startswith("$L"):
                op2 = op2.replace("L", "-")
            elif op2.startswith("$P"):
                op2 = "$" + str(-int(op2[2:]) + 6 + self.parameters)
            elif op2.startswith("$R"):
                op2 = "$" + str(6 + self.parameters)

            code.append("move {0} r{1}".format(op2, self.regDict[opmrl_op2]))
            opmrl_op2 = "r{0}".format(self.regDict[opmrl_op2])  

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
            if op2 in self.writeVals.keys():
                opmr_op2 = "r" + str(self.writeVals[op2])
            else:
                regVar = self.temporaryAllocate()
                code.append("move {0} r{1}".format(op2, self.regDict[regVar])) 
                opmr_op2 = "r" + str(self.regDict[regVar])   
                self.writeVals[op2] = self.regDict[regVar] 
        elif not op2.startswith("$"):
            opmr_op2 = op2
            self.declDict[opmr_op2] = ""
        elif op2.startswith("$L"):
            opmr_op2 = op2.replace("L", "-")
        elif op2.startswith("$P"):
            opmr_op2 = "$" + str(-int(op2[2:]) + 6 + self.parameters)
        elif op2.startswith("$R"):
            opmr_op2 = "$" + str(6 + self.parameters)
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

    def jsr(self, IRLine):
        lineSplit = IRLine.split(" ")
        label = lineSplit[1]
        code = []

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
        lineSplit = IRLine.split(" ")
        code = []
        if len(lineSplit) == 2:
            op1 = lineSplit[1]
            if op1.replace(".", "").replace("-", "").isdigit():
                value = op1
            elif not op1.startswith("$"):
                value = op1         
            elif op1.startswith("$L"):
                value = op1.replace("L", "-")
            elif op1.startswith("$P"):
                value = "$" + str(-int(op1[2:]) + 6 + self.parameters)
            elif op1.startswith("$R"):
                value = "$" + str(6 + self.parameters)
            else:
                self.registerAllocate(op1)
                value = "r{0}".format(self.regDict[op1])
            code.append("push {0}".format(value))
        else:
            code.append("push")

        self.tinyCode += "\n".join(code) + "\n"

    def pop(self, IRLine):
        lineSplit = IRLine.split(" ")
        code = []
        if len(lineSplit) == 2:
            op1 = lineSplit[1]
            if not op1.startswith("$"):
                value = op1            
            elif op1.startswith("$L"):
                value = op1.replace("L", "-")
            elif op1.startswith("$P"):
                value = "$" + str(-int(op1[2:]) + 6 + self.parameters)
            elif op1.startswith("$R"):
                value = "$" + str(6 + self.parameters)
            else:
                self.registerAllocate(op1)
                value = "r{0}".format(self.regDict[op1])
            code.append("pop {0}".format(value))
        else:
            code.append("pop")

        self.tinyCode += "\n".join(code) + "\n"

    def ret(self, IRLine):
        code = []
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
        self.tinyCode += "\n".join(code) + "\n"

    def errorFunct(self, IRLine):
        pass