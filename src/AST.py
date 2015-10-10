__author__ = 'gupta158, jalliger'

import sys
from enum import Enum

class AST():
	
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
			self.Left.printPostOrder()
		if self.Right is not None:
			self.Right.printPostOrder()
		self.printNodeInfo()

	def printNodeInfo(self):
		print("POP, value = {0}, LRType = {1}, type={2}".format(self.value, self.LRType, self.nodeType))


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


class ASTMath(AST):
	def __init__(self, opcode, nodeType=None, LRType=None, code=None, tempReg=None ):
		self.opcode = opcode
		super().__init__(self, nodeType, LRType, code, tempReg)

	def printNodeInfo(self):
		print("MATHPOP, opcode = {0}, LRType = {1}, type={2}".format(self.opcode, self.LRType, self.nodeType))
