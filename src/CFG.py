from IR import *

class OpDefinitions():
	comparisonOps = ["GEI", "GEF", "LEI", "LEF", "LTI", "LTF", "GTI", "GTF", "EQI", "EQF", "NEI", "NEF"]
	unconditionalJumpOps = ["JUMP"]    


class CFG():

	def __init__(self, functCode):
		self.stmtList = functCode.rstrip('\n').split('\n')
		self.CFGNodeList = []
		self.labelsLineNum = {}
		for lineNum in range(0, len(self.stmtList)):
			stmt = self.stmtList[lineNum]
			cfgNode = (CFGNode(stmt, lineNum))
			if cfgNode.op == "LABEL":
				self.labelsLineNum[cfgNode.lineSplit[1]] = lineNum
			self.CFGNodeList.append(cfgNode)

	def removeLinesWithNoPredecessors(self):
		nodesToRemove = []
		for cfgNodeIndex in range(1, len(self.CFGNodeList)):
			cfgNode = self.CFGNodeList[cfgNodeIndex]

			if len(cfgNode.predecessors) == 0:
				nodesToRemove.append(cfgNode)
				for successiveNodeLineNum in cfgNode.successors:
					self.CFGNodeList[successiveNodeLineNum].predecessors.remove((cfgNodeIndex))

		for nodeToRemove in nodesToRemove:
			self.CFGNodeList.remove(nodeToRemove)		

		self.fixLineNumbers()

	def getCode(self):
		return IRLinesArray.createIRString(self.CFGNodeList)


	def fixLineNumbers(self):
		for cfgNodeIndex in range(0, len(self.CFGNodeList)):
			cfgNode = self.CFGNodeList[cfgNodeIndex]
			cfgNode.lineNum = cfgNodeIndex


	def populateNodeInfo(self):
		for cfgNode in self.CFGNodeList:
			cfgNode.populateSuccessors(self.labelsLineNum)
			for successiveNodeLineNum in cfgNode.successors:
				self.CFGNodeList[successiveNodeLineNum].predecessors.append(cfgNode.lineNum)

	def printGraph(self):
		for cfgNode in self.CFGNodeList:
			print("Node {0}, stmt = {1} , predecessors = {2} , successors = {3}  ".format(cfgNode.lineNum, cfgNode.line, str(cfgNode.predecessors), str(cfgNode.successors)))
		return				


class CFGNode(IRLineObject):
	def __init__(self, line, lineNum):
		self.predecessors = []
		self.successors = []
		super().__init__(line, lineNum)

	def populateInformation(self):
		self.populatePredecessors()
		self.populateSuccessors()
		return

	def addPredecessor(self, lineNum):
		self.predecessors.append(lineNum)
		return

	def populateSuccessors(self, labelsLineNum):

		if self.op in OpDefinitions.unconditionalJumpOps:
			self.successors.append(labelsLineNum[self.lineSplit[1]])

		elif self.op in OpDefinitions.comparisonOps:
			self.successors.append(self.lineNum + 1)
			self.successors.append(labelsLineNum[self.lineSplit[3]])

		elif self.op == "RET":
			pass

		else:
			self.successors.append(self.lineNum + 1)

		return

	def __eq__(self, other):
	    return self.lineNum == other.lineNum