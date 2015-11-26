from IR import *

class CFG():

    def __init__(self, functCode):
        self.stmtList = functCode.rstrip('\n').split('\n')
        self.CFGNodeList = []
        self.labelsLineNum = {}
        for lineNum in range(0, len(self.stmtList)):
            stmt = self.stmtList[lineNum]
            cfgNode = (CFGNode(stmt, lineNum))
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
        self.populateNodeInfo()

    def getCode(self):
        return IRLinesArray.createIRString(self.CFGNodeList)


    def fixLineNumbers(self):
        for cfgNodeIndex in range(0, len(self.CFGNodeList)):
            cfgNode = self.CFGNodeList[cfgNodeIndex]
            cfgNode.lineNum = cfgNodeIndex


    def populateNodeInfo(self):
        self.labelsLineNum = {}
        for cfgNode in self.CFGNodeList:
            cfgNode.successors = []
            cfgNode.predecessors = []
            if cfgNode.op == "LABEL":
                self.labelsLineNum[cfgNode.lineSplit[1]] = cfgNode.lineNum

        for cfgNode in self.CFGNodeList:
            cfgNode.populateSuccessors(self.labelsLineNum)
            for successiveNodeLineNum in cfgNode.successors:
                self.CFGNodeList[successiveNodeLineNum].predecessors.append(cfgNode.lineNum)

    def emptyNodeLists(self):
        for cfgNode in self.CFGNodeList:
            cfgNode.genList      = []
            cfgNode.killList     = []
            cfgNode.inList       = []
            cfgNode.outList      = []
            cfgNode.changed      = True

    def runLivenessAnalysis(self, globalVariables):
        self.emptyNodeLists()
        for cfgNode in self.CFGNodeList:
            if cfgNode.op == "JSR":
                cfgNode.genList.extend(globalVariables)

            elif cfgNode.op in ["LABEL", "RET", "LINK", "JUMP"]:
                # continue
                pass

            elif cfgNode.op in ["WRITEI", "WRITEF", "PUSH"]:
                if len(cfgNode.lineSplit) == 2:
                    if not cfgNode.lineSplit[1].replace(".", "").replace("-", "").isdigit():
                        cfgNode.genList.append(cfgNode.lineSplit[1])

            elif cfgNode.op in ["READ", "POP"]:
                if len(cfgNode.lineSplit) == 2:
                    cfgNode.killList.append(cfgNode.lineSplit[1])

            elif cfgNode.op in OpDefinitions.comparisonOps:
                if not cfgNode.lineSplit[1].replace(".", "").replace("-", "").isdigit():
                    cfgNode.genList.append(cfgNode.lineSplit[1])
                if not cfgNode.lineSplit[2].replace(".", "").replace("-", "").isdigit():
                    cfgNode.genList.append(cfgNode.lineSplit[2])

            elif cfgNode.op in OpDefinitions.mathIntOps or cfgNode.op in OpDefinitions.mathFloatOps:
                if not cfgNode.lineSplit[1].replace(".", "").replace("-", "").isdigit():
                    cfgNode.genList.append(cfgNode.lineSplit[1])
                if not cfgNode.lineSplit[2].replace(".", "").replace("-", "").isdigit():
                    cfgNode.genList.append(cfgNode.lineSplit[2])
                cfgNode.killList.append(cfgNode.lineSplit[3])

            elif cfgNode.op in ["STOREI", "STOREF"]:
                if not cfgNode.lineSplit[1].replace(".", "").replace("-", "").isdigit():
                    cfgNode.genList.append(cfgNode.lineSplit[1])
                cfgNode.killList.append(cfgNode.lineSplit[2])


        changed = True
        while changed:
            changed = False
            for cfgNodeIndex in range(len(self.CFGNodeList)-1, -1, -1):
                cfgNode = self.CFGNodeList[cfgNodeIndex]
                oldOutList = cfgNode.outList            
                oldInList = cfgNode.inList          

                cfgNode.outList = []
                cfgNode.inList = []
                for successorIndex in cfgNode.successors:
                    successorNode = self.CFGNodeList[successorIndex]
                    print("START nodeNum = {0}, successorNodenum = {1}".format(cfgNode.lineNum, successorNode.lineNum))
                    print(cfgNode.outList)
                    print(successorNode.inList)
                    cfgNode.outList = CFGNode.unionLists(cfgNode.outList, successorNode.inList)
                    print(cfgNode.outList)
                    print("END")

                if cfgNode.op == "RET":
                    cfgNode.outList.extend(globalVariables)

                cfgNode.inList = list(cfgNode.outList)
                for killVar in cfgNode.killList:
                    if killVar in cfgNode.outList: 
                        cfgNode.inList.remove(killVar)
                cfgNode.inList = CFGNode.unionLists(cfgNode.inList, cfgNode.genList)
                if not changed:
                    changed = len(set(cfgNode.inList).intersection(oldInList)) != len(cfgNode.inList)
                if not changed:
                    changed = len(set(cfgNode.outList).intersection(oldOutList)) != len(cfgNode.outList)


    def printGraphWithNodeLists(self):
        for cfgNode in self.CFGNodeList:
            print("Node {0}, stmt = {1} , predecessors = {2} , successors = {3}".format(cfgNode.lineNum, cfgNode.line, str(cfgNode.predecessors), str(cfgNode.successors)))
            print("\t\t genList = {0} , killList = {1}".format(cfgNode.genList, cfgNode.killList))
            print("\t\t inList = {0} , outList = {1}".format(cfgNode.inList, cfgNode.outList))

        return          

    def printGraph(self):
        for cfgNode in self.CFGNodeList:
            print("Node {0}, stmt = {1} , predecessors = {2} , successors = {3}  ".format(cfgNode.lineNum, cfgNode.line, str(cfgNode.predecessors), str(cfgNode.successors)))
        return              


class CFGNode(IRLineObject):
    def __init__(self, line, lineNum):
        self.predecessors = []
        self.successors   = []
        self.genList      = []
        self.killList     = []
        self.inList       = []
        self.outList      = []
        self.changed      = True
        super().__init__(line, lineNum)

    def populateInformation(self):
        self.populatePredecessors()
        self.populateSuccessors()
        return

    def addPredecessor(self, lineNum):
        self.predecessors.append(lineNum)
        return

    def populateSuccessors(self, labelsLineNum):

        if self.op == "JUMP":
            self.successors.append(labelsLineNum[self.lineSplit[1]])

        elif self.op in OpDefinitions.comparisonOps:
            self.successors.append(self.lineNum + 1)
            self.successors.append(labelsLineNum[self.lineSplit[3]])

        elif self.op == "RET":
            pass

        else:
            self.successors.append(self.lineNum + 1)

        return

    def unionLists(list1, list2):
        result = list(list1)
        for el2 in list2:
            if el2 not in result:
                result.append(el2)

        return result

    def intersectLists(list1, list2):
        result = []
        for el1 in list1:
            if el1 in list2:
                result.append(el1)

        return result

    def __eq__(self, other):
        return self.lineNum == other.lineNum

