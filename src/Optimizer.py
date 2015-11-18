from antlr4 import *
from LittleExprParser import LittleExprParser
from LittleExprListener import LittleExprListener
from AST import *
import copy

#TODO : a = 20 -> 1 move
#       redundant moves for only 1 temp
class Optimizer():  
    opsThatChangeReg = ["STOREI", "STOREF", "ADDI", "ADDF", "SUBI", "SUBF", "MULTI", "MULTF", "DIVI", "DIVF", "STOREI", "STOREF", "READI", "READF", "POP"]
    opsThatDontChangeReg = ["WRITEI", "WRITEF","PUSH"]
    opsComparison = ["GEI", "GEF", "LEI", "LEF", "LTI", "LTF", "GTI", "GTF", "EQI", "EQF", "NEI", "NEF"]
            
    def __init__(self, IRcode):
        self.IRcode = IRcode
        self.Regs = {}

    def optimize(self):
        lines = self.IRcode.rstrip().split("\n")
        IRLines = self.CreateLineObjects(lines)

        while 1:
            oldIR = self.createNewIR(IRLines)

            IRLines = self.CreateLineObjects(self.createNewIR(IRLines).rstrip().split("\n"))
            IRLines = self.removeRedundantLabels(IRLines)

            IRLines = self.CreateLineObjects(self.createNewIR(IRLines).rstrip().split("\n"))
            IRLines = self.substituteIncDec(IRLines)

            # IRLines = self.CreateLineObjects(self.createNewIR(IRLines).rstrip().split("\n"))
            # IRLines = self.checkConstants(IRLines)

            # IRLines = self.CreateLineObjects(self.createNewIR(IRLines).rstrip().split("\n"))
            # IRLines = self.CSE(IRLines)
            
            # IRLines = self.CreateLineObjects(self.createNewIR(IRLines).rstrip().split("\n"))
            # IRLines = self.simplifyMoves(IRLines)

            # IRLines = self.CreateLineObjects(self.createNewIR(IRLines).rstrip().split("\n"))            
            # IRLines = self.reuseRegisters(IRLines)

            # print(";AAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
            # print(self.createNewIR(IRLines))
            # IRLines = self.CreateLineObjects(self.createNewIR(IRLines).rstrip().split("\n"))            
            # IRLines = self.removeUnecessaryStores(IRLines)
                        
            # print(";After reduce")
            # print(self.createNewIR(IRLines))

            # IRLines = self.CreateLineObjects(self.createNewIR(IRLines).rstrip().split("\n"))            
            # IRLines = self.removeUnnecessaryConditions(IRLines)

            if self.createNewIR(IRLines) == oldIR:
                break   


        # print(";AAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
        # print(self.createNewIR(IRLines))
        # IRLines = self.CreateLineObjects(self.createNewIR(IRLines).rstrip().split("\n"))
        # IRLines = self.reduceRegisters(IRLines)

        # IRLines = self.CreateLineObjects(self.createNewIR(IRLines).rstrip().split("\n"))
        # IRLines = self.mapMemoryToRegisters(IRLines)
        # print(";After reduce")
        # print(self.createNewIR(IRLines))
        return self.createNewIR(IRLines)


    def substituteIncDec(self, IRLines):
        newIRLines    = []
        store1Line    = False
        storeLineTemp = -1
        subLine       = False
        addLine       = False
        opLineVar     = -1
        opLineTemp    = -1

        # ;STOREI 1 $T5
        # ;SUBI i $T5 $T6
        # ;STOREI $T6 i
        for IRLine in IRLines:
            lineIsFinalStore = (IRLine.op == "STOREI") and (IRLine.lineSplit[1] == opLineTemp) and (IRLine.lineSplit[2] == opLineVar)
            if store1Line and addLine and lineIsFinalStore:
                newIRLines.pop()
                newIRLines.pop()
                newIRLines.append(IRLineObject("INCI {0}".format(IRLine.lineSplit[2])))
                continue

            elif store1Line and subLine and lineIsFinalStore:
                newIRLines.pop()
                newIRLines.pop()
                newIRLines.append(IRLineObject("DECI {0}".format(IRLine.lineSplit[2])))
                continue


            if IRLine.op == "ADDI":
                if store1Line:
                    if IRLine.lineSplit[2] == storeLineTemp:
                        opLineVar = IRLine.lineSplit[1]
                        opLineTemp = IRLine.lineSplit[3]
                        addLine = True
                    else:
                        store1Line = False

            elif IRLine.op == "SUBI":
                if store1Line:
                    if IRLine.lineSplit[2] == storeLineTemp:
                        opLineVar = IRLine.lineSplit[1]
                        opLineTemp = IRLine.lineSplit[3]
                        subLine = True
                    else:
                        store1Line = False
            elif IRLine.op == "STOREI" and IRLine.lineSplit[1] == "1":
                store1Line = True
                storeLineTemp = IRLine.lineSplit[2]

            else:
                store1Line = False
                subLine    = False
                addLine    = False

            newIRLines.append(IRLine)




        return newIRLines


    def removeRedundantLabels(self, IRLines):
        newIRLines = []
        labelsDict = {}

        lastLineIsLabel = False
        lastLabelNum = -1
        for IRLine in IRLines:
            lineIsLabel = IRLine.op == "LABEL"
            if not lineIsLabel: 
                lastLineIsLabel = lineIsLabel
                continue

            labelNum = IRLine.lineSplit[1]
            if lastLineIsLabel and lineIsLabel:
                labelsDict[labelNum] = lastLabelNum
            elif lineIsLabel:
                lastLabelNum = labelNum

            lastLineIsLabel = lineIsLabel

        for IRLine in IRLines:
            lineIsLabel = IRLine.op == "LABEL"
            if lineIsLabel:
                if IRLine.lineSplit[1] in labelsDict.keys():
                    continue

            if IRLine.op in Optimizer.opsComparison:
                if IRLine.lineSplit[3] in labelsDict.keys():
                    IRLine.lineSplit[3] = labelsDict[IRLine.lineSplit[3]]
                    IRLine.line = " ".join(IRLine.lineSplit)
            elif IRLine.op == "JUMP":
                if IRLine.lineSplit[1] in labelsDict.keys():
                    IRLine.lineSplit[1] = labelsDict[IRLine.lineSplit[1]]
                    IRLine.line = " ".join(IRLine.lineSplit)

            newIRLines.append(IRLine)

        return newIRLines


    def removeUnnecessaryConditions(self, IRLines):
        def checkNumConstant(num):
            if num.replace(".", "").replace("-", "").isdigit():
                return True
            return False

        newIRLines = []
        labels = []
        deleteCodeType = [] 
        exitLabel = []
        for IRLine in IRLines:
            if IRLine.op == "LABEL":
                labels.append(IRLine.lineSplit[1])

            if len(deleteCodeType) > 0:
                if deleteCodeType[-1] == 1:
                    if IRLine.op == "LABEL":
                        if IRLine.lineSplit[1] == exitLabel[-1]:
                            deleteCodeType.pop()
                    continue
                elif deleteCodeType[-1] == 2:
                    if IRLine.op == "LABEL":
                        if IRLine.lineSplit[1] == exitLabel[-1]:
                            if newIRLines[-1].op == "JUMP":
                                deleteCodeType[-1] = 1
                                exitLabel.pop()
                                exitLabel.append(newIRLines[-1].lineSplit[1])
                                newIRLines.pop()
                            else:
                                deleteCodeType.pop()
                                exitLabel.pop()

                    continue


            if IRLine.op in Optimizer.opsComparison:
                opr1      = IRLine.lineSplit[1]
                opr2      = IRLine.lineSplit[2]
                labelName = IRLine.lineSplit[3]

                if checkNumConstant(opr1) and checkNumConstant(opr2) and labelName not in labels:
                    exitLabel.append(labelName)
                    if IRLine.op in ["GEI", "GEF"]:
                        if opr1 >= opr2:
                            deleteCodeType.append(1)
                        else:
                            deleteCodeType.append(2)
                    if IRLine.op in ["LEI", "LEF"]:
                        if opr1 <= opr2:
                            deleteCodeType.append(1)
                        else:
                            deleteCodeType.append(2)
                    if IRLine.op in ["EQI", "EQI"]:
                        if opr1 == opr2:
                            deleteCodeType.append(1)
                        else:
                            deleteCodeType.append(2)
                    if IRLine.op in ["NEI", "NEF"]:
                        if opr1 != opr2:
                            deleteCodeType.append(1)
                        else:
                            deleteCodeType.append(2)
                    if IRLine.op in ["LTI", "LTF"]:
                        if opr1 < opr2:
                            deleteCodeType.append(1)
                        else:
                            deleteCodeType.append(2)
                    if IRLine.op in ["GTI", "GTF"]:
                        if opr1 > opr2:
                            deleteCodeType.append(1)
                        else:
                            deleteCodeType.append(2)
                    continue
                # else:
                #     deleteCodeType
            newIRLines.append(IRLine)

        return IRLines

    def markLastChangedLines(self, IRlines):
        for IRline in IRlines:
            for reg in IRline.Regs:
                if not reg in self.Regs.keys():
                    self.Regs[reg] = Register(reg, IRline.lineNum, IRline.lineNum)
                self.Regs[reg].lastUsed = IRline.lineNum

            if IRline.op in self.opsThatChangeReg:
                reg = IRline.lineSplit[-1]
                if not reg.startswith("$"):
                    continue
                self.Regs[reg].lastChanged = IRline.lineNum

    def removeUnecessaryStores(self, IRLines):
        def checkLastChanged():
            reg1 = IRLine.lineSplit[2]
            if reg1.startswith("$") and self.Regs[reg1].lastChanged == IRLine.lineNum:
                return True
            return False

        def checkIfRegChanged(firstReg):
            if IRLines[lineNumber].op in self.opsThatChangeReg and firstReg == IRLines[lineNumber].Regs[-1]:
                return True
            return False                

        self.Regs = {}
        self.markLastChangedLines(IRLines)
        mappingDict = {}
        recycledRegisters = []
        newIRLines = []
        for IRLine in IRLines:
            isStore     = IRLine.lineNum and IRLine.op in ["STOREI", "STOREF"]
            if isStore and checkLastChanged() and IRLine.lineSplit[1].startswith("$"):
                regChanged = False
                for lineNumber in range(IRLine.lineNum+1, self.Regs[IRLine.lineSplit[2]].lastUsed+1):
                    if checkIfRegChanged(IRLine.lineSplit[1]):
                        regChanged = True

                if regChanged:
                    newIRLines.append(IRLine)
                else:
                    reg1 = IRLine.lineSplit[1]
                    if reg1 in mappingDict.keys():
                        regresult   = IRLine.lineSplit[2]
                        mappingDict[regresult] = mappingDict[reg1]
                    else:
                        reg1 = IRLine.lineSplit[1]
                        regresult   = IRLine.lineSplit[2]
                        mappingDict[regresult] = reg1
            else: 
                regArray = IRLine.Regs
                for reg in regArray:
                    if reg in mappingDict.keys():
                        IRLine.updateLine(reg, mappingDict[reg])
                newIRLines.append(IRLine)
        return newIRLines

    def reuseRegisters(self, IRLines):
        def checkLastUsed():
            reg1 = IRLine.lineSplit[1]
            if reg1.startswith("$") and self.Regs[reg1].lastUsed == IRLine.lineNum:
                return True
            return False

        self.Regs = {}
        self.markLines(IRLines)
        mappingDict = {}
        recycledRegisters = []
        newIRLines = []
        for IRLine in IRLines:
            isStore     = IRLine.lineNum and IRLine.op in ["STOREI", "STOREF"]
            if isStore and checkLastUsed() and IRLine.lineSplit[2].startswith("$"):
                reg1 = IRLine.lineSplit[1]
                if reg1 in mappingDict.keys():
                    regresult   = IRLine.lineSplit[2]
                    mappingDict[regresult] = mappingDict[reg1]
                else:
                    reg1 = IRLine.lineSplit[1]
                    regresult   = IRLine.lineSplit[2]
                    mappingDict[regresult] = reg1
            else: 
                regArray = IRLine.Regs
                for reg in regArray:
                    if reg in mappingDict.keys():
                        IRLine.updateLine(reg, mappingDict[reg])
                newIRLines.append(IRLine)
        return newIRLines

    def mapMemoryToRegisters(self, IRLines):
        newIRLines = []
        ignoreOPS = ["STORES", "WRITES", "JUMP", "LABEL"]
        compOPS = ["GEI", "GEF", "LEI", "LEF", "EQI", "EQF", "GTI", "GTF", "NEI", "NEF", "LTI", "LTF"]

        varDict = {}
        maxTValue = -1
        for IRLine in IRLines:
            if IRLine.op in ignoreOPS:
                continue
            
            lastOp = len(IRLine.lineSplit) if IRLine.op not in compOPS else 3
            for i in range(1, lastOp):
                if IRLine.lineSplit[i].replace(".", "").replace("-", "").isdigit():
                    continue
                if IRLine.lineSplit[i].startswith("$"):
                    tValue = int(IRLine.lineSplit[i].split("$")[1][1:])
                    if tValue > maxTValue:
                        maxTValue = tValue

                    continue
                varDict[IRLine.lineSplit[i]] = ""

        for key in varDict.keys():
            varDict[key] = "$T" + str(maxTValue + 1)
            maxTValue    += 1

        for IRLine in IRLines:
            if IRLine.op in ignoreOPS:
                newIRLines.append(IRLine)
                continue
            
            lastOp = len(IRLine.lineSplit) if IRLine.op not in compOPS else 3
            for i in range(1, lastOp):
                if IRLine.lineSplit[i].replace(".", "").replace("-", "").isdigit():
                    continue
                if IRLine.lineSplit[i].startswith("$"):
                    continue
                IRLine.lineSplit[i] = varDict[IRLine.lineSplit[i]]
            IRLine.line = " ".join(IRLine.lineSplit)
            newIRLines.append(IRLine)

        return IRLines

    def CreateLineObjects(self, lines):
        IRLines = []
        count = 0
        for line in lines:
            IRLines.append(IRLineObject(line, count))
            count += 1
        return IRLines

    def markLines(self, IRlines):
        for IRline in IRlines:
            for reg in IRline.Regs:
                if not reg in self.Regs.keys():
                    self.Regs[reg] = Register(reg, IRline.lineNum, IRline.lineNum)
                self.Regs[reg].lastUsed = IRline.lineNum

    def reduceRegisters(self, IRLines):
        self.Regs = {}
        self.markLines(IRLines)
        mappingDict = {}
        recycledRegisters = []
        for IRLine in IRLines:
            regArray = IRLine.Regs
            popRegs = []
            # print("NEWLINE")
            # print(" ".join(IRLine.lineSplit))
            # print(regArray)
            for reg in regArray:
                # print("firstUsed = {0}, lastUsed = {1}, lineNum = {2}, reg = {3}".format(self.Regs[reg].firstUsed, self.Regs[reg].lastUsed, IRLine.lineNum, reg))
                if self.Regs[reg].firstUsed == IRLine.lineNum:
                    if len(recycledRegisters) != 0:
                        mappingDict[reg] = recycledRegisters.pop()
 
                elif self.Regs[reg].lastUsed == IRLine.lineNum:
                    recyledRegToAppend = reg
                    if reg in mappingDict.keys():
                        recyledRegToAppend = mappingDict[reg]
                        popRegs.append(reg)

                    if recyledRegToAppend not in recycledRegisters:
                        recycledRegisters.append(recyledRegToAppend)
                if reg in mappingDict.keys():
                    IRLine.updateLine(reg, mappingDict[reg])
            for reg in set(popRegs):
                mappingDict.pop(reg)

            # print("MAP")
            # print(mappingDict)
            # print("RECYCLED")
            # print(recycledRegisters)
        return IRLines

    def simplifyMoves(self, IRLines):
        simpIRLines = []
        lastWasMove = False
        linenum = 0 
        lastlinesplit = []
        for line in IRLines:
            #splitline = line.line.split(" ")
            lineIsMove = line.op in ["STOREI", "STOREF"]
            if lineIsMove and line.lineSplit[1] == line.lineSplit[2]:
                continue
            if lastWasMove and lineIsMove and line.lineSplit[1].startswith("$") and lastlinesplit[2] == line.lineSplit[1]:
                simpIRLines[-1].removeTemp(line.lineSplit[1], line.lineSplit[2])
                #simpIRLines.append(line)
            else:
                simpIRLines.append(line)
                simpIRLines[-1].linenum = linenum
                linenum += 1

            lastWasMove = lineIsMove
            lastlinesplit = line.lineSplit
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

    def checkConstants(self, IRLines):
        def ifConstant(value):
            if value in regConstantDict.keys() and value not in ignoreSet and regConstantDict[value][1]:
                return True

            return False

        def invalidate(value):
            if value in regConstantDict.keys(): 
                regConstantDict[value][1] = 0

        def compareDicts(oldDict, newDict):
            storeLines = []
            keysList = []
            for key in oldDict.keys():
                if oldDict[key][0] != newDict[key][0] and newDict[key][1]:
                    storeLines.append(IRLineObject("STOREI {0} {1}".format(key, newDict[key])))
                    keysList.append(key)
                    oldDict[key][1] = 0
            return storeLines

        ignoreSets   = self.findLoops(IRLines)
        ignoreSetsIf = self.findIfs(IRLines)

        ignoreSet = set()
        activeLoops = set()
        newIRLines = []
        regConstantDict = {}
        oldLineisComp = False
        isLoop = False
        oldLabel = ""
        ignoreSet = set()

        tempDicts = []
        for label in ignoreSets.keys():
           ignoreSet |= ignoreSets[label][1]

        for IRLine in IRLines:
            newIRLines.append(IRLine)
            regArray = IRLine.Regs
            isStore = IRLine.op in ["STOREI", "STOREF"]
            isRead  = IRLine.op in ["READI", "READF"]

            #this check brakes
            #if isLoop:
            #   if IRLine.op == "LABEL" and IRLine.line.split(" ")[1] == oldLabel:
            #      isLoop = False
            #   continue

            # have no idea what this does
            #if oldLineisComp and IRLine.op == "LABEL":
            #    isLoop = True
            #    oldLineisComp = False
            #    continue

            splitline = IRLine.line.split(" ")

            if IRLine.op == "LABEL" and splitline[1] in ignoreSetsIf.keys():
                if splitline[1] in ignoreSetsIf.keys():
                    activeLoops.discard(splitline[1])
                    ignoreSet = set()
                    for label in activeLoops:
                        ignoreSet |= ignoreSetsIf[label][1] 


            if isStore:
                if splitline[1].replace(".", "").replace("-", "").isdigit() and splitline[2] not in ignoreSet:
                    regConstantDict[splitline[2]] = [splitline[1], 1]
                    newIRLines.pop()
                elif ifConstant(splitline[1]):
                    if splitline[2] in ignoreSet:
                        lineToFix = newIRLines.pop()
                        lineToFix.lineSplit[1] = regConstantDict[lineToFix.lineSplit[1]][0]
                        lineToFix.line = ' '.join(lineToFix.lineSplit)
                        lineToFix = IRLineObject(lineToFix.line, lineToFix.lineNum)
                        newIRLines.append(lineToFix)
                    else:
                        regConstantDict[splitline[2]] = [regConstantDict[splitline[1]][0], 1]
                        newIRLines.pop()
                else:
                    invalidate(splitline[2])
                    continue
            elif isRead:
                invalidate(splitline[1])



            isMath = IRLine.op in ["ADDI", "SUBI", "MULTI", "DIVI"]

            if isMath and ifConstant(splitline[1]) and ifConstant(splitline[2]):
                outVal = 0
                if IRLine.op.startswith("ADD"):
                    outVal = float(regConstantDict[splitline[1]][0]) + float(regConstantDict[splitline[2]][0]) 
                elif IRLine.op.startswith("SUB"):
                    outVal = float(regConstantDict[splitline[1]][0]) - float(regConstantDict[splitline[2]][0]) 
                elif IRLine.op.startswith("MULT"):
                    outVal = float(regConstantDict[splitline[1]][0]) * float(regConstantDict[splitline[2]][0]) 
                elif IRLine.op.startswith("DIV"):
                    outVal = float(regConstantDict[splitline[1]][0]) / float(regConstantDict[splitline[2]][0]) 


                if IRLine.op.endswith("I"):
                    outVal = int(outVal)
                    regConstantDict[splitline[3]] = [outVal, 1]

                else:
                    regConstantDict[splitline[3]] = [outVal, 1]
                newIRLines.pop()

            else:
                if ifConstant(splitline[1]):
                    IRLine.line = IRLine.line.replace(splitline[1], str(regConstantDict[splitline[1]][0]), 1)
                    if splitline[1] in IRLine.Regs:
                        IRLine.Regs.remove(splitline[1])
                    if isMath:
                        invalidate(splitline[3])

                if len(splitline) >= 3 and ifConstant(splitline[2]):
                    IRLine.line = IRLine.line.replace(splitline[2], str(regConstantDict[splitline[2]][0]), 1)
                    if splitline[2] in IRLine.Regs:
                        IRLine.Regs.remove(splitline[2])
                    if isMath:
                        invalidate(splitline[3])


            # if IRLine.op in Optimizer.opsComparison and len(tempDicts) > 0:
            #     oldDict = tempDicts[-1][1]
            #     newStoreLines = compareDicts(oldDict, regConstantDict)
            #     currLine = newIRLines.pop()
            #     newIRLines.extend(newStoreLines)
            #     newIRLines.append(currLine)

            #     print(self.createNewIR(newStoreLines))
            #     print(IRLine.line)

            # if (IRLine.op == "LABEL" and IRLine.lineSplit[1] == tempDicts[-1][0] and len(tempDicts) > 0 and IRLines[IRLine.lineNum - 1].op != "JUMP"):
            #     oldDict = tempDicts[-1][1]
            #     newStoreLines = compareDicts(oldDict, regConstantDict)
            #     currLine = newIRLines.pop()
            #     newIRLines.extend(newStoreLines)
            #     newIRLines.append(currLine)
            #     regConstantDict = oldDict

            #     tempDicts.pop()
            #     print(self.createNewIR(newStoreLines))
            #     print(IRLine.line)


            # if IRLine.op == "JUMP" and len(tempDicts) > 0:
            #     oldDict = tempDicts[-1][1]
            #     newStoreLines = compareDicts(oldDict, regConstantDict)
            #     currLine = newIRLines.pop()
            #     newIRLines.extend(newStoreLines)
            #     newIRLines.append(currLine)
            #     regConstantDict = oldDict

            #     print(self.createNewIR(newStoreLines))
            #     print(IRLine.line)


            # if IRLine.op in Optimizer.opsComparison and IRLine.lineSplit[3] in ignoreSetsIf.keys():
            #     tempDicts.append((IRLine.lineSplit[3], regConstantDict.copy()))

                
            # oldLineisComp = IRLine.op in ["GTI", "GTF", "LTI", "LTF", "EQI", "EQF", "NEI", "NEF", "GEI", "GEF", "LEI", "LEF"] 
            # oldLabel = IRLine.line.split(' ')[3] if oldLineisComp else ""


            
            if IRLine.op in ["GTI", "GTF", "LTI", "LTF", "EQI", "EQF", "NEI", "NEF", "GEI", "GEF", "LEI", "LEF"] and splitline[3] in ignoreSetsIf.keys():
                ignoreSet |= ignoreSetsIf[splitline[3]][1] #Cant just invalidate because items not seen yet
                activeLoops.add(splitline[3])
                print(ignoreSet)
                


            if IRLine.op == "JUMP" and splitline[1] in ignoreSetsIf.keys():
                ignoreSet |= ignoreSetsIf[splitline[1]][1] #Cant just invalidate because items not seen yet
                activeLoops.add(splitline[1])
                print(ignoreSet)

        for line in newIRLines:
            #print(line.line)
            pass
        
        return newIRLines

    def findLoops(self, IRLines):
        def addToAllSets(result):
            if not result.startswith("$"):
                for key, value in possNonConstant.items():
                    value.add(result)


        nonConstants = {}
        possNonConstant = {}
        for IRLine in IRLines:
            regArray = IRLine.Regs
            # isStore = IRLine.op in ["STOREI", "STOREF"]
            # isRead  = IRLine.op in ["READI", "READF"]
            # isLabel  = IRLine.op == "LABEL"
            # isJump = IRLine.op in ["GTI", "GTF", "LTI", "LTF", "EQI", "EQF", "NEI", "NEF", "GEI", "GEF", "LEI", "LEF", "JUMP"] 
            splitline = IRLine.line.split(" ")

            if IRLine.op in ["ADDI", "SUBI", "MULTI", "DIVI","ADDF", "SUBF", "MULTF", "DIVF"]:
                if splitline[1].replace(".", "").replace("-", "").isdigit() and splitline[2].replace(".", "").replace("-", "").isdigit():
                    pass
                else:
                    addToAllSets(splitline[3])
                continue

            if IRLine.op in ["STOREI", "STOREF"]:#if not a literal constant, we might need to ignore it
                if splitline[1].replace(".", "").replace("-", "").isdigit():
                    pass
                else:
                    addToAllSets(splitline[2])
                continue

            if IRLine.op in ["READI", "READF"]:
                addToAllSets(splitline[1])
                continue

            
            if IRLine.op == "LABEL": # find a new label, this may loop back here
                possNonConstant[splitline[1]] =set()
                continue

                
            if IRLine.op in ["GTI", "GTF", "LTI", "LTF", "EQI", "EQF", "NEI", "NEF", "GEI", "GEF", "LEI", "LEF"]:
                if splitline[3] in possNonConstant.keys(): #if it is a loop back, it is a problem
                    nonConstants[splitline[3]] = (IRLine.lineNum ,possNonConstant[splitline[3]].copy())
                continue

            if IRLine.op == "JUMP":
                if splitline[1] in possNonConstant.keys(): 
                    nonConstants[splitline[1]] = (IRLine.lineNum, possNonConstant[splitline[3]].copy())
                continue
        return nonConstants

    def findIfs(self, IRLines):
        def addToAllSets(result):
            for key, value in possNonConstant.items():
                value.add(result)

        nonConstants = {}
        possNonConstant = {}
        for IRLine in reversed(IRLines):
            regArray = IRLine.Regs
            # isStore = IRLine.op in ["STOREI", "STOREF"]
            # isRead  = IRLine.op in ["READI", "READF"]
            # isLabel  = IRLine.op == "LABEL"
            # isJump = IRLine.op in ["GTI", "GTF", "LTI", "LTF", "EQI", "EQF", "NEI", "NEF", "GEI", "GEF", "LEI", "LEF", "JUMP"] 
            splitline = IRLine.line.split(" ")

            if IRLine.op in ["ADDI", "SUBI", "MULTI", "DIVI","ADDF", "SUBF", "MULTF", "DIVF"]:
                if splitline[1].replace(".", "").replace("-", "").isdigit() and splitline[2].replace(".", "").replace("-", "").isdigit():
                    pass
                else:
                    addToAllSets(splitline[3])


            elif IRLine.op in ["STOREI", "STOREF"]:#if not a literal constant, we might need to ignore it
                if splitline[1].replace(".", "").replace("-", "").isdigit():
                    pass
                else:
                    addToAllSets(splitline[2])
            
            elif IRLine.op in ["READI", "READF"]:
                addToAllSets(splitline[1])
                        
            elif IRLine.op == "LABEL": # find a new label, this may loop back here
                possNonConstant[splitline[1]] = set()
                              
            elif IRLine.op in ["GTI", "GTF", "LTI", "LTF", "EQI", "EQF", "NEI", "NEF", "GEI", "GEF", "LEI", "LEF"]:
                if splitline[3] in possNonConstant.keys(): #if it is a loop back, it is a problem
                    nonConstants[splitline[3]] = (IRLine.lineNum, possNonConstant[splitline[3]].copy())
                

            elif IRLine.op == "JUMP":
                if splitline[1] in possNonConstant.keys(): 
                    nonConstants[splitline[1]] = (IRLine.lineNum, possNonConstant[splitline[1]].copy())

        return nonConstants

    def CSE(self, IRLines):
        def removeResult(result):
            keysToPop = []
            for key in knownResults.keys():
                if result == key[1] or result == key[2]:
                    keysToPop.append(key)
            for key in keysToPop:
                knownResults.pop(key)

            pass

        newIRLines = []
        Mathops = ["ADDI", "SUBI", "MULTI", "DIVI", "ADDF", "SUBF", "MULTF", "DIVF"]
        ASSop = ["ADDI", "MULTI"]
        storer = ["STOREI", "STOREF"]
        reader = ["READI", "READF"]
        knownResults = {}

        for IRLine in IRLines:
            if IRLine.op in Mathops:
                #check if can be replaced with store ellse add it to the list
                opperands = [IRLine.lineSplit[1], IRLine.lineSplit[2]]
                if IRLine.op in ASSop:
                    opperands.sort()
                operation = (IRLine.op, opperands[0], opperands[1])

                if operation in knownResults.keys():
                    newLine = "STORE{0} {1} {2}".format(IRLine.op[-1], knownResults[operation], IRLine.lineSplit[3])
                    newIRLine = IRLineObject(newLine, IRLine.lineNum)
                    newIRLines.append(newIRLine)
                else:
                    knownResults[operation] = IRLine.lineSplit[3]
                    newIRLines.append(IRLine)

                removeResult(IRLine.lineSplit[3])
            elif IRLine.op in storer:
                removeResult(IRLine.lineSplit[2])
                newIRLines.append(IRLine)
            elif IRLine.op in reader:
                removeResult(IRLine.lineSplit[1])
                newIRLines.append(IRLine)
            else:
                newIRLines.append(IRLine)
        return newIRLines


class Register():

    def __init__(self, regName, firstUsed=0, lastUsed=-1):
        self.regName = regName
        self.firstUsed = firstUsed
        self.lastUsed = lastUsed
        self.lastChanged = -1


class IRLineObject():

    def __init__(self, line, lineNum=-1):
        self.line = line
        self.Regs = []
        self.op = ""
        self.newLine = line
        self.assignVariables()
        self.lineNum = lineNum

    def assignVariables(self):
        self.lineSplit = self.line.rstrip().split(" ")
        self.op = self.lineSplit[0]
        for i in self.lineSplit:
            if i.startswith("$"):
                self.Regs.append(i)

    def updateLine(self, reg, newReg):
        self.line = self.line.replace(reg, newReg, 1)
        #numReg = self.Regs.count(reg)
        #for i in range(0, numReg):
        self.Regs = [x if (x != reg) else newReg for x in self.Regs]

    def removeTemp(self, reg, replacement):
        self.lineSplit[2] = replacement
        self.line = " ".join(self.lineSplit)
        # self.line = self.line.replace(reg, replacement)
        self.Regs.remove(reg)

