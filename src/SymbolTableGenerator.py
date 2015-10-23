from antlr4 import *
from LittleExprParser import LittleExprParser
from LittleExprListener import LittleExprListener
from AST import *
from TinyGenerator import *
from Optimizer import *

# This class defines a complete listener for a parse tree produced by LittleExprParser.
class SymbolTableGenerator(LittleExprListener):

    def __init__(self):
        super().__init__()
        self.block = 1
        self.symbolTable = []
        self.printSymbolTable = []
        self.ASTStack  = []

	# Enter a parse tree produced by LittleExprParser#program.
    def enterProgram(self, ctx:LittleExprParser.ProgramContext):
        self.printSymbolTable.append("Symbol table GLOBAL\r")
        self.symbolTable.append({})
        pass

	# Exit a parse tree produced by LittleExprParser#program.
    def exitProgram(self, ctx:LittleExprParser.ProgramContext):
        #print("\n".join(self.printSymbolTable))
        self.symbolTable.pop()
        pass

	# Enter a parse tree produced by LittleExprParser#func_decl.
    def enterFunc_decl(self, ctx:LittleExprParser.Func_declContext):
       self.printSymbolTable.append("\nSymbol table {0}\r".format(ctx.getChild(2).getText()))
       self.symbolTable.append({})
       pass

	# Exit a parse tree produced by LittleExprParser#func_decl.
    def exitFunc_decl(self, ctx:LittleExprParser.Func_declContext):
        self.symbolTable.pop()
        pass

	# Enter a parse tree produced by LittleExprParser#if_stmt.
    def enterIf_stmt(self, ctx:LittleExprParser.If_stmtContext):
        self.printSymbolTable.append("\nSymbol table BLOCK {0}\r".format(self.block))
        self.symbolTable.append({})
        self.block += 1
        pass

	# Enter a parse tree produced by LittleExprParser#else_part.
    def enterElse_part(self, ctx:LittleExprParser.Else_partContext):
        self.symbolTable.pop()  # Pop if block
        self.printSymbolTable.append("\nSymbol table BLOCK {0}\r".format(self.block))
        self.symbolTable.append({})
        self.block += 1
        pass

	# Exit a parse tree produced by LittleExprParser#else_part.
    def exitElse_part(self, ctx:LittleExprParser.Else_partContext):
        if int(ctx.getChildCount()) == 0:
            return
        self.symbolTable.pop()
        pass


	# Enter a parse tree produced by LittleExprParser#for_stmt.
    def enterFor_stmt(self, ctx:LittleExprParser.For_stmtContext):
        self.printSymbolTable.append("\nSymbol table BLOCK {0}\r".format(self.block))
        self.symbolTable.append({})
        self.block += 1
        pass


	# Enter a parse tree produced by LittleExprParser#param_decl_list.
    def enterString_decl(self, ctx:LittleExprParser.Param_decl_listContext):
        identifier = ctx.getChild(1).getText()
        value = ctx.getChild(3).getText()
        self.addSymbolToTable(identifier, "STRING", value)
        self.printSymbolTable.append("name {0} type STRING value {1}\r".format(identifier, value))
        pass

    # Enter a parse tree produced by LittleExprParser#param_decl_list.
    def enterVar_decl(self, ctx:LittleExprParser.Param_decl_listContext):
        varType = ctx.getChild(0).getText()
        idListTree = ctx.getChild(1)
        identifier = idListTree.getChild(0).getText()

        self.addSymbolToTable(identifier, varType)
        self.printSymbolTable.append("name {0} type {1}\r".format(identifier,varType))

        idTailTree = idListTree.getChild(1)        
        while(idTailTree.getChildCount() != 0):
            identifier = idTailTree.getChild(1).getText()
            self.addSymbolToTable(identifier, varType)
            self.printSymbolTable.append("name {0} type {1}\r".format(identifier,varType))
            idTailTree = idTailTree.getChild(2)
        pass

    # Enter a parse tree produced by LittleExprParser#param_decl_list.
    def enterParam_decl(self, ctx:LittleExprParser.Param_decl_listContext):
        varType = ctx.getChild(0).getText()
        identifier = ctx.getChild(1).getChild(0).getText()
        self.addSymbolToTable(identifier, varType)
        self.printSymbolTable.append("name {0} type {1}\r".format(identifier,varType))


    ###########################################################################################################
    # AST/Code Generation
    #
    ###########################################################################################################
                
    # Exit a parse tree produced by LittleExprParser#func_body.
    def exitFunc_body(self, ctx:LittleExprParser.Func_bodyContext):
        self.ASTStack[-1].generateCode()
        print(self.ASTStack[-1].code)
        # #Pre Optimized code
        # self.tinyGenerator = TinyGenerator(self.ASTStack[-1].code)
        # self.tinyGenerator.generate()
        # self.printTinyIR(comment = 1)

        # #Optimized code
        # self.optimizer = Optimizer(self.ASTStack[-1].code)
        # self.ASTStack[-1].code = self.optimizer.optimize()
        # self.tinyGenerator = TinyGenerator(self.ASTStack[-1].code)
        # self.tinyGenerator.generate()
        # self.printTinyIR()
        # #self.printNewestAST()
        pass

   
    # Exit a parse tree produced by LittleExprParser#if_stmt.
    def exitIf_stmt(self, ctx:LittleExprParser.If_stmtContext):
        ifNode = ASTIf()        
        
        # If else does not exist
        if ctx.else_part() is not None and ctx.else_part().getText():
            self.symbolTable.pop()
            ifNode.ElseNode = self.ASTStack.pop()

        ifNode.ThenNode = self.ASTStack.pop()
        ifNode.CondNode = self.ASTStack.pop()
        ifNode.setupNode()

        self.ASTStack.append(ifNode)
               
        pass


    # Exit a parse tree produced by LittleExprParser#for_stmt.
    def exitFor_stmt(self, ctx:LittleExprParser.For_stmtContext):
        self.symbolTable.pop()

        forNode = ASTFor()

        forNode.StmtNode      = self.ASTStack.pop()
        forNode.IncrNode      = self.ASTStack.pop()
        forNode.CondNodeStart = self.ASTStack.pop()
        forNode.InitNode      = self.ASTStack.pop()

        forNode.setupNode()
        self.ASTStack.append(forNode)
        return


    # Exit a parse tree produced by LittleExprParser#cond.
    def exitCond(self, ctx:LittleExprParser.CondContext):
        exprNode2  = self.ASTStack.pop()
        compopNode = self.ASTStack.pop()
        exprNode1  = self.ASTStack.pop()

        compopNode.Left = exprNode1
        compopNode.Right = exprNode2
        self.ASTStack.append(compopNode)
        pass

    # Exit a parse tree produced by LittleExprParser#mulop.
    def exitCompop(self, ctx:LittleExprParser.CompopContext):
        if ctx.LT() is not None:
            self.ASTStack.append(ASTCond(opcode=COMPOP.inverseOP(COMPOP.LT), LRType=LRTYPE.RTYPE))
        elif ctx.GT() is not None:
            self.ASTStack.append(ASTCond(opcode=COMPOP.inverseOP(COMPOP.GT), LRType=LRTYPE.RTYPE))
        elif ctx.EQU() is not None:
            self.ASTStack.append(ASTCond(opcode=COMPOP.inverseOP(COMPOP.EQU), LRType=LRTYPE.RTYPE))
        elif ctx.NEQ() is not None:
            self.ASTStack.append(ASTCond(opcode=COMPOP.inverseOP(COMPOP.NEQ), LRType=LRTYPE.RTYPE))
        elif ctx.LEQ() is not None:
            self.ASTStack.append(ASTCond(opcode=COMPOP.inverseOP(COMPOP.LEQ), LRType=LRTYPE.RTYPE))
        elif ctx.GEQ() is not None:
            self.ASTStack.append(ASTCond(opcode=COMPOP.inverseOP(COMPOP.GEQ), LRType=LRTYPE.RTYPE))

    # Enter a parse tree produced by LittleExprParser#stmt_list.
    def exitStmt_list(self, ctx:LittleExprParser.Stmt_listContext):
        if int(ctx.getChildCount()) == 0:
            return

        stmtListNode = ASTStmt()
        stmtNode = self.ASTStack.pop()
        stmtListNode.Right = stmtNode
        stmtListNode.Left = None

        if ctx.stmt_list() is not None and ctx.stmt_list().getText():
            stmtListNode.Left = self.ASTStack.pop()

        self.ASTStack.append(stmtListNode)
        return


    # Exit a parse tree produced by LittleExprParser#write_stmt.
    def exitWrite_stmt(self, ctx:LittleExprParser.Write_stmtContext):
        idListTree = ctx.id_list()
        identifier = idListTree.identifier()
        writeNode = ASTWrite()
        writeNode.Left = self.CreateIdentifierNode(identifier)

        writeNode2 = writeNode
        idTailTree = idListTree.id_tail()     
        while(idTailTree.getChildCount() != 0):
            identifier = idTailTree.identifier()
            writeNode.Right = ASTWrite()
            writeNode = writeNode.Right
            writeNode.Left = self.CreateIdentifierNode(identifier)
            idTailTree = idTailTree.id_tail() 

        writeNode.Right = None
        self.ASTStack.append(writeNode2)
        return

    # Exit a parse tree produced by LittleExprParser#read_stmt.
    def exitRead_stmt(self, ctx:LittleExprParser.Read_stmtContext):
        idListTree = ctx.id_list()
        identifier = idListTree.identifier()
        readNode = ASTRead()
        readNode.Left = self.CreateIdentifierNode(identifier)

        readNode2 = readNode
        idTailTree = idListTree.id_tail()     
        while(idTailTree.getChildCount() != 0):
            identifier = idTailTree.identifier()
            readNode.Right = ASTRead()
            readNode = readNode.Right
            readNode.Left = self.CreateIdentifierNode(identifier)
            idTailTree = idTailTree.id_tail() 

        readNode.Right = None
        self.ASTStack.append(readNode2)
        return

    # Enter a parse tree produced by LittleExprParser#assign_stmt.
    def exitAssign_expr(self, ctx:LittleExprParser.Assign_stmtContext):
        identifierNode = ctx.getChild(0)
        exprNode = self.ASTStack.pop()

        assignNode = ASTAssign()
        assignNode.Left = self.CreateIdentifierNode(identifierNode)
        assignNode.Right = exprNode
        self.ASTStack.append(assignNode)
        return

    # Exit a parse tree produced by LittleExprParser#expr.
    def exitExpr(self, ctx:LittleExprParser.ExprContext):
        factorNode = self.ASTStack.pop()    
        if ctx.expr_prefix() is not None and ctx.expr_prefix().getText():
            exprPrefix = self.ASTStack.pop() 
            exprPrefix.Right = factorNode
            self.ASTStack.append(exprPrefix)
        else:
            self.ASTStack.append(factorNode)

        return

    # Exit a parse tree produced by LittleExprParser#expr_prefix.
    def exitExpr_prefix(self, ctx:LittleExprParser.Expr_prefixContext):
        if int(ctx.getChildCount()) == 0:
            return
        addopNode   = self.ASTStack.pop()       
        factorNode  = self.ASTStack.pop()       
        if ctx.expr_prefix() is not None and ctx.expr_prefix().getText():
            exprPrefix = self.ASTStack.pop() 
            exprPrefix.Right = factorNode
            addopNode.Left = exprPrefix
        else:
            addopNode.Left = factorNode

        self.ASTStack.append(addopNode)
        return

    # Exit a parse tree produced by LittleExprParser#factor.
    def exitFactor(self, ctx:LittleExprParser.FactorContext):   
        postFixExpr = self.ASTStack.pop()    
        if ctx.factor_prefix() is not None and ctx.factor_prefix().getText():
            factorPrefix = self.ASTStack.pop() 
            factorPrefix.Right = postFixExpr
            self.ASTStack.append(factorPrefix)
        else:
            self.ASTStack.append(postFixExpr)
        return

    # Exit a parse tree produced by LittleExprParser#factor_prefix.
    def exitFactor_prefix(self, ctx:LittleExprParser.Factor_prefixContext):
        if int(ctx.getChildCount()) == 0:
            return
        mulopNode   = self.ASTStack.pop()       
        postFixExpr = self.ASTStack.pop()       
        if ctx.factor_prefix() is not None and ctx.factor_prefix().getText():
            factorPrefix = self.ASTStack.pop() 
            factorPrefix.Right = postFixExpr
            mulopNode.Left = factorPrefix
        else:
            mulopNode.Left = postFixExpr

        self.ASTStack.append(mulopNode)
        return

    # Enter a parse tree produced by LittleExprParser#primary.
    def exitPrimary(self, ctx:LittleExprParser.PrimaryContext):
        if ctx.identifier() is not None:
            identifierNode = ctx.identifier()
            self.ASTStack.append(self.CreateIdentifierNode(identifierNode))
        elif ctx.INTLITERAL() is not None:
            INTLITERAL = ctx.INTLITERAL()
            self.ASTStack.append(self.CreateINTLITERALNode(INTLITERAL))
        elif ctx.FLOATLITERAL() is not None:
            FLOATLITERAL = ctx.FLOATLITERAL()
            self.ASTStack.append(self.CreateFLOATLITERALNode(FLOATLITERAL))
        # Else case handled by default
        return

    # Exit a parse tree produced by LittleExprParser#mulop.
    def exitMulop(self, ctx:LittleExprParser.MulopContext):
        if ctx.MUL() is not None:
            self.ASTStack.append(ASTMath(opcode=MATHOP.MUL, LRType=LRTYPE.RTYPE))
        else:
            self.ASTStack.append(ASTMath(opcode=MATHOP.DIV, LRType=LRTYPE.RTYPE))

    # Exit a parse tree produced by LittleExprParser#addop.
    def exitAddop(self, ctx:LittleExprParser.AddopContext):
        if ctx.ADD() is not None:
            self.ASTStack.append(ASTMath(opcode=MATHOP.ADD, LRType=LRTYPE.RTYPE))
        else:
            self.ASTStack.append(ASTMath(opcode=MATHOP.SUB, LRType=LRTYPE.RTYPE))


    ###########################################################################################    
    # Helper Functions
    #
    ###########################################################################################

    # Create Empty Node
    def CreateEmptyNode(self, ctx:LittleExprParser.IdentifierContext):
        astNode = AST()
        return astNode        
        pass

    # Create Identifier Node
    def CreateIdentifierNode(self, ctx:LittleExprParser.IdentifierContext):
        identifier = ctx.getChild(0).getText()
        identifierSymbol = self.GetSymbolFromSymbolTable(identifier)
        identifierType = ""
        value = ""

        if identifierSymbol[0] == "INT":
            identifierType = NODETYPE.INTLITERAL
            value = identifier
        elif identifierSymbol[0] == "FLOAT":
            identifierType = NODETYPE.FLOATLITERAL
            value = identifier
        elif identifierSymbol[0] == "STRING":
            identifierType = NODETYPE.STRINGLITERAL
            value = identifierSymbol[1]

        astNode = AST(value=value, LRType=LRTYPE.LTYPE, nodeType=identifierType, tempReg=value)
        return astNode

    # Create INTLITERAL Node
    def CreateINTLITERALNode(self, token):
        astNode = AST(token.getText(), LRType=LRTYPE.RTYPE, nodeType=NODETYPE.INTLITERAL)
        return astNode

    # Create FLOATLITERAL Node
    def CreateFLOATLITERALNode(self, token):
        astNode = AST(token.getText(), LRType=LRTYPE.RTYPE, nodeType=NODETYPE.FLOATLITERAL)
        return astNode
        
    # Add variable to identifier
    def addSymbolToTable(self, identifier, varType, value=None):
        if(identifier in self.symbolTable[-1]):
            raise SyntaxError(identifier) 
        self.symbolTable[-1][identifier] = (varType, value)

    # Print symbol table stack
    def printSymbolTableStack(self):
        elementsOnStack = len(self.symbolTable)
        for i in range(1, elementsOnStack+1):
            print("Stack Element {0}".format(-1*i))
            print(self.symbolTable[-1 * i])

    # Get Symbol from table
    def GetSymbolFromSymbolTable(self, identifier):
        elementsOnStack = len(self.symbolTable)
        for i in range(1, elementsOnStack+1):
            if identifier in self.symbolTable[-1 * i].keys():
                return self.symbolTable[-1 * i][identifier]
        raise(ElementOutOfScopeError(identifier))

    # Print newest AST
    def printNewestAST(self):
        print("<Expr>")
        self.ASTStack[-1].printInOrder()
        print("</Expr>")

    def printTinyIR(self, comment=0):
        if comment:
            print(";Pre optimized code")
            print(";;;IR code")
            print(";;;" + self.ASTStack[-1].code.replace("\n", "\n;;;") + "tinycode")  
            print(";;" + self.tinyGenerator.tinyCode.replace("\n", "\n;;"))
            print(";END OF Pre optimized code")
        else:
            print(";IR code")
            print(";" + self.ASTStack[-1].code.replace("\n", "\n;") + "tinycode")  
            print(self.tinyGenerator.tinyCode)
        



class ElementOutOfScopeError(Exception):
    pass