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
		self.code 	= code
		self.tempReg 	= tempReg


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
		# if(self.Left.LRType == LRTYPE.LTYPE):
		# 	if(self.Left.nodeType == NODETYPE.FLOATLITERAL):
		# 		lCode = "STOREF {0} $T{1} \n".format(self.Left.value, AST.tempRegNum)
		# 		self.Left.tempReg = "$T{0}".format(AST.tempRegNum)
		# 		AST.tempRegNum += 1
		# 	elif(self.Left.nodeType == NODETYPE.INTLITERAL):
		# 		lCode = "STOREI {0} $T{1} \n".format(self.Left.value, AST.tempRegNum)
		# 		self.Left.tempReg = "$T{0}".format(AST.tempRegNum)
		# 		AST.tempRegNum += 1

		# if(self.Right.LRType == LRTYPE.LTYPE):
		# 	if(self.Right.nodeType == NODETYPE.FLOATLITERAL):
		# 		rCode = "STOREF {0} $T{1} \n".format(self.Right.value, AST.tempRegNum)
		# 		self.Right.tempReg = "$T{0}".format(AST.tempRegNum)
		# 		AST.tempRegNum += 1
		# 	elif(self.Right.nodeType == NODETYPE.INTLITERAL):
		# 		rCode = "STOREI {0} $T{1} \n".format(self.Right.value, AST.tempRegNum)
		# 		self.Right.tempReg = "$T{0}".format(AST.tempRegNum)
		# 		AST.tempRegNum += 1
			
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
		print("ASSIGN, value = {0}, LRType = {1}, type={2} \n".format(self.value, self.LRType, self.nodeType))

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

class MATHOP(Enum):
	ADD 	= 1
	SUB		= 2
	MUL		= 3
	DIV		= 4


class LRTYPE(Enum):
	LTYPE 	= 1
	RTYPE	= 2

class NODETYPE(Enum):
	INTLITERAL 		= 1
	FLOATLITERAL 	= 2
	STRINGLITERAL	= 3


