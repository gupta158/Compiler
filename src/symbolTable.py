__author__ = 'gupta158, jalliger'

import sys
from antlr4 import *
from antlr4.InputStream import InputStream
from LittleExprLexer import LittleExprLexer
from LittleExprParser import LittleExprParser
from LittleExprErrorStrategy import LittleExprErrorStrategy
from SymbolTableGenerator import SymbolTableGenerator


class symbolTable:

	#TODO: Put type of tree here 
	def __init__(self, parseTree, parser):
		self.parseTree = parseTree
		self.parser = parser

	def generateTable(self):
		print(self.parseTree.toStringTree(recog=self.parser))
