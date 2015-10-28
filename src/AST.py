__author__ = 'gupta158, jalliger'

#TODO:
# String literal stuff?
# READ/WRITE
#

import sys
from enum import Enum

class TempReg():
    regNum = 0

class AST():
    tempRegNum = 1
    codeLabelNum = 1
    
    #nodeType
    # INTLITERAL    => 1
    # FLOATLITERAL  => 2

    #LR TYPE
    # L => 1
    # R => 2
    def __init__(self, value=None, nodeType=None, LRType=None, code=None, tempReg=None ):
        self.Left = None
        self.Right = None
        self.value = value
        self.nodeType = nodeType
        self.LRType = LRType
        self.code   = code
        self.tempReg    = tempReg


    def printInOrder(self):
        if self.Left is not None:
            print("<left>")
            self.Left.printInOrder()
            print("</left>")

        print("<node>")
        self.printNodeInfo()
        print("</node>")

        if self.Right is not None:
            print("<right>")
            self.Right.printInOrder()
            print("</right>")

        return

    def printPostOrder(self):
        if self.Left is not None:
            print("<left>")
            self.Left.printPostOrder()
            print("</left>")
        if self.Right is not None:
            print("<right>")
            self.Right.printPostOrder()
            print("</right>")
        print("<node>")
        self.printNodeInfo()
        print("</node>")

    def printNodeInfo(self):
        print("BASE, value = {0}, LRType = {1}, type={2}".format(self.value, self.LRType, self.nodeType))

    def generateCode(self):
        lCode = ""
        rCode = ""
        if self.Left is not None:
            lCode = self.Left.generateCode()
        if self.Right is not None:
            rCode = self.Right.generateCode()   
        return self.generateSelfCode(lCode, rCode)

    def generateSelfCode(self, lCode, rCode):
        self.code = ""
        if(self.LRType == LRTYPE.RTYPE):
            if(self.nodeType == NODETYPE.FLOATLITERAL):
                self.code = "STOREF {0} $T{1} \n".format(self.value, AST.tempRegNum)
                self.tempReg = "$T{0}".format(AST.tempRegNum)
                AST.tempRegNum += 1
            elif(self.nodeType == NODETYPE.INTLITERAL):
                self.code = "STOREI {0} $T{1} \n".format(self.value, AST.tempRegNum)
                self.tempReg = "$T{0}".format(AST.tempRegNum)
                AST.tempRegNum += 1
        return self.code
        

class ASTMath(AST):
    def __init__(self, opcode, value=None, nodeType=None, LRType=None, code=None, tempReg=None ):
        self.opcode = opcode
        super().__init__("MATH", nodeType, LRType, code, tempReg)

    def printNodeInfo(self):
        print("MATHPOP, opcode = {0}, LRType = {1}, type={2} \n".format(self.opcode, self.LRType, self.nodeType))

    def generateSelfCode(self, lCode, rCode):
        newCode = ""    
            
        if(self.Left.nodeType == NODETYPE.INTLITERAL):
            self.nodeType = NODETYPE.INTLITERAL
            if(self.opcode == MATHOP.ADD):
                newCode = "ADDI {0} {1} $T{2} \n".format(self.Left.tempReg, self.Right.tempReg, AST.tempRegNum)
                self.tempReg = "$T{0}".format(AST.tempRegNum)
                AST.tempRegNum += 1
            elif(self.opcode == MATHOP.SUB):
                newCode = "SUBI {0} {1} $T{2} \n".format(self.Left.tempReg, self.Right.tempReg, AST.tempRegNum)
                self.tempReg = "$T{0}".format(AST.tempRegNum)
                AST.tempRegNum += 1
            elif(self.opcode == MATHOP.MUL):
                newCode = "MULTI {0} {1} $T{2} \n".format(self.Left.tempReg, self.Right.tempReg, AST.tempRegNum)
                self.tempReg = "$T{0}".format(AST.tempRegNum)
                AST.tempRegNum += 1
            elif(self.opcode == MATHOP.DIV):
                newCode = "DIVI {0} {1} $T{2} \n".format(self.Left.tempReg, self.Right.tempReg, AST.tempRegNum)
                self.tempReg = "$T{0}".format(AST.tempRegNum)
                AST.tempRegNum += 1

        elif(self.Left.nodeType == NODETYPE.FLOATLITERAL):
            self.nodeType = NODETYPE.FLOATLITERAL
            if(self.opcode == MATHOP.ADD):
                newCode = "ADDF {0} {1} $T{2} \n".format(self.Left.tempReg, self.Right.tempReg, AST.tempRegNum)
                self.tempReg = "$T{0}".format(AST.tempRegNum)
                AST.tempRegNum += 1
            elif(self.opcode == MATHOP.SUB):
                newCode = "SUBF {0} {1} $T{2} \n".format(self.Left.tempReg, self.Right.tempReg, AST.tempRegNum)
                self.tempReg = "$T{0}".format(AST.tempRegNum)
                AST.tempRegNum += 1
            elif(self.opcode == MATHOP.MUL):
                newCode = "MULTF {0} {1} $T{2} \n".format(self.Left.tempReg, self.Right.tempReg, AST.tempRegNum)
                self.tempReg = "$T{0}".format(AST.tempRegNum)
                AST.tempRegNum += 1
            elif(self.opcode == MATHOP.DIV):
                newCode = "DIVF {0} {1} $T{2} \n".format(self.Left.tempReg, self.Right.tempReg, AST.tempRegNum)
                self.tempReg = "$T{0}".format(AST.tempRegNum)
                AST.tempRegNum += 1

        self.code = lCode + rCode + newCode
        return self.code


class ASTAssign(AST):
    def __init__(self, value=None, nodeType=None, LRType=None, code=None, tempReg=None ):
        super().__init__(value="Assign", nodeType=nodeType, LRType=LRType, code=code, tempReg=tempReg)

    def printNodeInfo(self):
        print("ASSIGN, value = {0}, LRType = {1}, type={2}, tempReg = {3} \n".format(self.value, self.LRType, self.nodeType, self.tempReg))

    def generateSelfCode(self, lCode, rCode):
        self.code = ""
        opRegValue = ""
        if self.Right.tempReg is not None:
            opRegValue = self.Right.tempReg
        else:   
            opRegValue = self.Right.value

        if(self.Right.nodeType == NODETYPE.INTLITERAL):
            self.code = rCode + "STOREI {0} {1} \n".format(opRegValue, self.Left.value)
        elif(self.Right.nodeType == NODETYPE.FLOATLITERAL):
            self.code = rCode + "STOREF {0} {1} \n".format(opRegValue, self.Left.value)
        return self.code


class ASTStmt(AST):
    def __init__(self, value=None, nodeType=None, LRType=None, code=None, tempReg=None ):
        super().__init__(value="Stmt", nodeType=nodeType, LRType=LRType, code=code, tempReg=tempReg)

    def printNodeInfo(self):
        print("STMT, value = {0}, LRType = {1}, type={2} \n".format(self.value, self.LRType, self.nodeType))

    def generateSelfCode(self, lCode, rCode):
        self.code = lCode
        if self.Right is not None:
            self.code = self.code + rCode
        return self.code


class ASTWrite(AST):
    def __init__(self, value=None, nodeType=None, LRType=None, code=None, tempReg=None, addStore=False, stringLiteral=None ):
        self.addStore = addStore
        self.stringLiteral = stringLiteral
        super().__init__(value="Write", nodeType=nodeType, LRType=LRType, code=code, tempReg=tempReg)

    def printNodeInfo(self):
        print("WRITE, value = {0}, LRType = {1}, type={2} \n".format(self.value, self.LRType, self.nodeType))

    def generateSelfCode(self, lCode, rCode):
        self.code = ""
        if(self.Left.nodeType == NODETYPE.INTLITERAL):
            self.code = "WRITEI {0} \n".format(self.Left.tempReg)
        elif(self.Left.nodeType == NODETYPE.FLOATLITERAL):
            self.code = "WRITEF {0} \n".format(self.Left.tempReg)
        elif(self.Left.nodeType == NODETYPE.STRINGLITERAL):
            if self.addStore:
                self.code = "STORES {0} {1}\n".format(self.stringLiteral, self.Left.tempReg)

            self.code += "WRITES {0} \n".format(self.Left.tempReg)
        if self.Right is not None:
            self.code = self.code + rCode
        return self.code


class ASTRead(AST):
    def __init__(self, value=None, nodeType=None, LRType=None, code=None, tempReg=None ):
        super().__init__(value="Read", nodeType=nodeType, LRType=LRType, code=code, tempReg=tempReg)

    def printNodeInfo(self):
        print("READ, value = {0}, LRType = {1}, type={2} \n".format(self.value, self.LRType, self.nodeType))

    def generateSelfCode(self, lCode, rCode):
        if(self.Left.nodeType == NODETYPE.INTLITERAL):
            self.code = "READI {0} \n".format(self.Left.tempReg)
        elif(self.Left.nodeType == NODETYPE.FLOATLITERAL):
            self.code = "READF {0} \n".format(self.Left.tempReg)
        if self.Right is not None:
            self.code = self.code + rCode
        return self.code


class ASTCond(AST):
    def __init__(self, opcode, value=None, nodeType=None, LRType=None, code=None, tempReg=None ):
        self.opcode = opcode
        self.endLabel = ""
        self.startLabel = ""

        super().__init__("COND", nodeType, LRType, code, tempReg)

    def printNodeInfo(self):
        print("COMPOP, opcode = {0}, LRType = {1}, type={2} \n".format(self.opcode, self.LRType, self.nodeType))

    def generateSelfCode(self, lCode, rCode):
        newCode = ""            

        rightRegValue = ""
        leftRegValue = ""

        if self.Right.tempReg is not None:
            rightRegValue = self.Right.tempReg
        else:   
            rightRegValue = self.Right.value

        if self.Left.tempReg is not None:
            leftRegValue = self.Left.tempReg
        else:   
            leftRegValue = self.Left.value
            
        if(self.Left.nodeType == NODETYPE.FLOATLITERAL):
            self.nodeType = NODETYPE.FLOATLITERAL
        else:
            self.nodeType = NODETYPE.INTLITERAL

        if(self.Left.nodeType == NODETYPE.INTLITERAL):
            if(self.opcode == COMPOP.LT):
                newCode = "LTI {0} {1} LABEL{2} \n".format(leftRegValue, rightRegValue, self.endLabel)
            elif(self.opcode == COMPOP.GT):
                newCode = "GTI {0} {1} LABEL{2} \n".format(leftRegValue, rightRegValue, self.endLabel)
            elif(self.opcode == COMPOP.EQ):
                newCode = "EQI {0} {1} LABEL{2} \n".format(leftRegValue, rightRegValue, self.endLabel)
            elif(self.opcode == COMPOP.NE):
                newCode = "NEI {0} {1} LABEL{2} \n".format(leftRegValue, rightRegValue, self.endLabel)
            elif(self.opcode == COMPOP.LE):
                newCode = "LEI {0} {1} LABEL{2} \n".format(leftRegValue, rightRegValue, self.endLabel)
            elif(self.opcode == COMPOP.GE):
                newCode = "GEI {0} {1} LABEL{2} \n".format(leftRegValue, rightRegValue, self.endLabel)
        else:
            if(self.opcode == COMPOP.LT):
                newCode = "LTF {0} {1} LABEL{2} \n".format(leftRegValue, rightRegValue, self.endLabel)
            elif(self.opcode == COMPOP.GT):
                newCode = "GTF {0} {1} LABEL{2} \n".format(leftRegValue, rightRegValue, self.endLabel)
            elif(self.opcode == COMPOP.EQ):
                newCode = "EQF {0} {1} LABEL{2} \n".format(leftRegValue, rightRegValue, self.endLabel)
            elif(self.opcode == COMPOP.NE):
                newCode = "NEF {0} {1} LABEL{2} \n".format(leftRegValue, rightRegValue, self.endLabel)
            elif(self.opcode == COMPOP.LE):
                newCode = "LEF {0} {1} LABEL{2} \n".format(leftRegValue, rightRegValue, self.endLabel)
            elif(self.opcode == COMPOP.GE):
                newCode = "GEF {0} {1} LABEL{2} \n".format(leftRegValue, rightRegValue, self.endLabel)


        self.code = lCode + rCode + newCode
        return self.code


class ASTIf(AST):
    def __init__(self, value=None, nodeType=None, LRType=None, code=None, tempReg=None ):
        self.CondNode      = None
        self.ThenNode      = None
        self.ElseNode      = None
        self.ElseLabelNode = None
        self.JumpNode      = None

        super().__init__("IF", nodeType, LRType, code, tempReg)

    def setupNode(self):
        self.ExitLabelNode = ASTLabel()
        self.CondNode.endLabel = self.ExitLabelNode.labelNum
        if self.ElseNode is not None:
            self.ElseLabelNode = ASTLabel()
            self.CondNode.endLabel = self.ElseLabelNode.labelNum
            self.JumpNode = ASTJump()
            self.JumpNode.labelNum = self.ExitLabelNode.labelNum

    def printNodeInfo(self):
        print("IF, value = {0}, LRType = {1}, type={2} \n".format(self.value, self.LRType, self.nodeType))

    def generateCode(self):
        condCode      = ""
        thenCode      = ""
        elseCode      = ""
        exitLabelCode = ""
        elseLabelCode = ""
        jumpCode      = ""

        if self.CondNode is not None:
            condCode = self.CondNode.generateCode()
        if self.JumpNode is not None:
            jumpCode = self.JumpNode.generateCode()
        if self.ThenNode is not None:
            thenCode = self.ThenNode.generateCode() 
        if self.ElseLabelNode is not None:
            elseLabelCode = self.ElseLabelNode.generateCode()
        if self.ElseNode is not None:
            elseCode = self.ElseNode.generateCode()
        if self.ExitLabelNode is not None:
            exitLabelCode = self.ExitLabelNode.generateCode()

        return self.generateSelfCode(condCode, thenCode, jumpCode, elseLabelCode, elseCode, exitLabelCode)

    def generateSelfCode(self, condCode, thenCode, jumpCode, elseLabelCode, elseCode, exitLabelCode):
        newCode = condCode      

        self.code = condCode + thenCode + jumpCode + elseLabelCode + elseCode + exitLabelCode
        return self.code


    def printInOrder(self):
        if self.CondNode is not None:
            print("<condNode>")
            self.CondNode.printInOrder()
            print("</condNode>")

        print("<node>")
        self.printNodeInfo()
        print("</node>")

        if self.ThenNode is not None:
            print("<thenNode>")
            self.ThenNode.printInOrder()
            print("</thenNode>")

        if self.ExitLabelNode is not None:
            print("<exitLabelNode>")
            self.ExitLabelNode.printInOrder()
            print("</exitLabelNode>")

        if self.ElseNode is not None:
            print("<elseNode>")
            self.ElseNode.printInOrder()
            print("</elseNode>")
        return


class ASTFor(AST):
    def __init__(self, value=None, nodeType=None, LRType=None, code=None, tempReg=None ):
        self.CondNodeStart = None
        self.InitNode      = None
        self.IncrNode      = None
        self.StmtNode      = None
        self.LoopLabelNode = None
        self.ExitLabelNode = None
        self.CondNodeEnd   = None

        super().__init__("FOR", nodeType, LRType, code, tempReg)

    def setupNode(self):
        self.LoopLabelNode = ASTLabel()
        self.ExitLabelNode = ASTLabel()
        self.CondNodeEnd   = ASTCond(opcode=COMPOP.inverseOP(self.CondNodeStart.opcode), LRType=LRTYPE.RTYPE)

        self.CondNodeEnd.Left       = self.CondNodeStart.Left
        self.CondNodeEnd.Right      = self.CondNodeStart.Right
        self.CondNodeStart.endLabel = self.ExitLabelNode.labelNum
        self.CondNodeEnd.endLabel   = self.LoopLabelNode.labelNum


    def printNodeInfo(self):
        print("FOR, value = {0}, LRType = {1}, type={2} \n".format(self.value, self.LRType, self.nodeType))

    def generateCode(self):
        condCodeStart = ""
        condCodeEnd   = ""
        initCode      = ""
        incrCode      = ""
        stmtCode      = ""
        exitLabelCode = ""
        loopLabelCode = ""

        if self.CondNodeStart is not None:
            condCodeStart = self.CondNodeStart.generateCode()
        if self.CondNodeEnd is not None:
            condCodeEnd = self.CondNodeEnd.generateCode()
        if self.InitNode is not None:
            initCode = self.InitNode.generateCode() 
        if self.IncrNode is not None:
            incrCode = self.IncrNode.generateCode()
        if self.StmtNode is not None:
            stmtCode = self.StmtNode.generateCode()
        if self.ExitLabelNode is not None:
            exitLabelCode = self.ExitLabelNode.generateCode()
        if self.LoopLabelNode is not None:
            loopLabelCode = self.LoopLabelNode.generateCode()

        return self.generateSelfCode(condCodeStart, condCodeEnd, initCode, incrCode, stmtCode, exitLabelCode, loopLabelCode)

    def generateSelfCode(self, condCodeStart, condCodeEnd, initCode, incrCode, stmtCode, exitLabelCode, loopLabelCode):
        self.code = initCode + condCodeStart + loopLabelCode + stmtCode + incrCode + condCodeEnd + exitLabelCode
        return self.code


    def printInOrder(self):

        if self.InitNode is not None:
            print("<initNode>")
            self.InitNode.printInOrder()
            print("</initNode>")

        if self.CondNodeStart is not None:
            print("<condNodeStart>")
            self.CondNodeStart.printInOrder()
            print("</condNodeStart>")

        print("<node>")
        self.printNodeInfo()
        print("</node>")

        if self.LoopLabelNode is not None:
            print("<loopLabelNode>")
            self.LoopLabelNode.printInOrder()
            print("</loopLabelNode>")

        if self.IncrNode is not None:
            print("<incrNode>")
            self.IncrNode.printInOrder()
            print("</incrNode>")

        if self.StmtNode is not None:
            print("<stmtNode>")
            self.StmtNode.printInOrder()
            print("</stmtNode>")

        if self.ExitLabelNode is not None:
            print("<exitLabelNode>")
            self.ExitLabelNode.printInOrder()
            print("</exitLabelNode>")

        if self.CondNodeEnd is not None:
            print("<condNodeEnd>")
            self.CondNodeEnd.printInOrder()
            print("</condNodeEnd>")

        return


class ASTLabel(AST):    

    def __init__(self, value=None, nodeType=None, LRType=None, code=None, tempReg=None ):
        super().__init__(value="LABEL", nodeType=nodeType, LRType=LRType, code=code, tempReg=tempReg)
        self.labelNum = AST.codeLabelNum
        AST.codeLabelNum += 1

    def printNodeInfo(self):
        print("LABEL, value = {0}, LRType = {1}, type={2}, labelNum = {0} \n".format(self.value, self.LRType, self.nodeType, self.labelNum ))

    def generateSelfCode(self, lCode, rCode):
        self.code = "LABEL LABEL{0} \n".format(self.labelNum)
        return self.code

class ASTJump(AST):    

    def __init__(self, value=None, nodeType=None, LRType=None, code=None, tempReg=None ):
        super().__init__(value="JUMP", nodeType=nodeType, LRType=LRType, code=code, tempReg=tempReg)
        self.labelNum = -1

    def printNodeInfo(self):
        print("JUMP, value = {0}, LRType = {1}, type={2}, labelNum = {0} \n".format(self.value, self.LRType, self.nodeType, self.labelNum ))

    def generateSelfCode(self, lCode, rCode):
        self.code = "JUMP LABEL{0} \n".format(self.labelNum)
        return self.code



class COMPOP(Enum):
    LT      = 1
    GT      = 2
    EQ      = 3
    NE      = 4
    LE      = 5
    GE      = 6

    def inverseOP(op):
        if op == COMPOP.LT:
            return COMPOP.GE
        elif op == COMPOP.GT:
            return COMPOP.LE
        elif op == COMPOP.EQ:
            return COMPOP.NE
        elif op == COMPOP.NE:
            return COMPOP.EQ
        elif op == COMPOP.LE:
            return COMPOP.GT
        elif op == COMPOP.GE:
            return COMPOP.LT
        pass


class MATHOP(Enum):
    ADD     = 1
    SUB     = 2
    MUL     = 3
    DIV     = 4


class LRTYPE(Enum):
    LTYPE   = 1
    RTYPE   = 2


class NODETYPE(Enum):
    INTLITERAL      = 1
    FLOATLITERAL    = 2
    STRINGLITERAL   = 3


