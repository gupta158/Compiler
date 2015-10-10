from antlr4 import *
from LittleExprParser import LittleExprParser
from LittleExprListener import LittleExprListener
from AST import *

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

	# Exit a parse tree produced by LittleExprParser#if_stmt.
    def exitIf_stmt(self, ctx:LittleExprParser.If_stmtContext):
        # If else does not exist
        if ctx.else_part() is not None:
            self.symbolTable.pop()
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
        self.symbolTable.pop()
        pass


	# Enter a parse tree produced by LittleExprParser#for_stmt.
    def enterFor_stmt(self, ctx:LittleExprParser.For_stmtContext):
        self.printSymbolTable.append("\nSymbol table BLOCK {0}\r".format(self.block))
        self.symbolTable.append({})
        self.block += 1
        pass

	# Exit a parse tree produced by LittleExprParser#for_stmt.
    def exitFor_stmt(self, ctx:LittleExprParser.For_stmtContext):
        self.symbolTable.pop()
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
    
    # Enter a parse tree produced by LittleExprParser#stmt_list.
    def enterStmt_list(self, ctx:LittleExprParser.Stmt_listContext):
        pass


    # Enter a parse tree produced by LittleExprParser#expr.
    def enterExpr(self, ctx:LittleExprParser.ExprContext):
        pass

    # Exit a parse tree produced by LittleExprParser#expr.
    def exitExpr(self, ctx:LittleExprParser.ExprContext):
        factorNode = self.ASTStack.pop()    
        if ctx.expr_prefix() is not None and ctx.expr_prefix().getText():
            exprPrefix = self.ASTStack.pop() 
            exprPrefix.Right = factorNode
            self.ASTStack.append(exprPrefix)
        else:
            self.ASTStack.append(factorNode)

        print(self.ASTStack[-1].printPostOrder())
        print(len(self.ASTStack))
        return


    # Enter a parse tree produced by LittleExprParser#expr_prefix.
    def enterExpr_prefix(self, ctx:LittleExprParser.Expr_prefixContext):
        pass

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

    # Enter a parse tree produced by LittleExprParser#factor.
    def enterFactor(self, ctx:LittleExprParser.FactorContext):
        pass
        #self.ASTStack.append(self.CreateEmptyNode(identifierNode))

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


    # Enter a parse tree produced by LittleExprParser#factor_prefix.
    def enterFactor_prefix(self, ctx:LittleExprParser.Factor_prefixContext):
        #self.ASTStack.append(self.CreateEmptyNode(identifierNode))
        pass

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

    # # Enter a parse tree produced by LittleExprParser#postfix_expr.
    # def enterPostfix_expr(self, ctx:LittleExprParser.Postfix_exprContext):
    #     self.ASTStack.append(self.CreateEmptyNode(identifierNode))

    # # Enter a parse tree produced by LittleExprParser#postfix_expr.
    # def exitPostfix_expr(self, ctx:LittleExprParser.Postfix_exprContext):


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
            self.ASTStack.append(self.CreateINTLITERALNode(FLOATLITERAL))
        # Else case handled by default
        #return self.CreatePrimaryNode(ctx)
        pass

    # Exit a parse tree produced by LittleExprParser#mulop.
    def exitMulop(self, ctx:LittleExprParser.MulopContext):
        if ctx.MUL() is not None:
            self.ASTStack.append(ASTMath(opcode=MATHOP.MUL, LRType=LRTYPE.RTYPE))
        else:
            self.ASTStack.append(ASTMath(opcode=MATHOP.DIV, LRType=LRTYPE.RTYPE))


    # Enter a parse tree produced by LittleExprParser#addop.
    def enterAddop(self, ctx:LittleExprParser.AddopContext):
        pass


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

    # Create Primary Node
    def CreatePrimaryNode(self, ctx:LittleExprParser.PrimaryContext):
        if ctx.identifier() is not None:
            identifierNode = ctx.identifier()
            return self.CreateIdentifierNode(identifierNode)
        elif ctx.INTLITERAL() is not None:
            INTLITERAL = ctx.INTLITERAL()
            return self.CreateINTLITERALNode(INTLITERAL)
        elif ctx.FLOATLITERAL() is not None:
            FLOATLITERAL = ctx.FLOATLITERAL()
            return self.CreateINTLITERALNode(FLOATLITERAL)
        #else:

        pass

    # Create Identifier Node
    def CreateIdentifierNode(self, ctx:LittleExprParser.IdentifierContext):
        astNode = AST(ctx.getChild(0).getText(), LRType=LRTYPE.LTYPE, nodeType=NODETYPE.INTLITERAL)
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