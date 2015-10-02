from antlr4 import *
from LittleExprParser import LittleExprParser
from LittleExprListener import LittleExprListener

# This class defines a complete listener for a parse tree produced by LittleExprParser.
class SymbolTableGenerator(LittleExprListener):

    def __init__(self):
        super().__init__()
        self.block = 1
        self.symbolTable = []
        self.printSymbolTable = []

	# Enter a parse tree produced by LittleExprParser#program.
    def enterProgram(self, ctx:LittleExprParser.ProgramContext):
        self.printSymbolTable.append("Symbol table GLOBAL\r")
        self.symbolTable.append({})
        pass

	# Exit a parse tree produced by LittleExprParser#program.
    def exitProgram(self, ctx:LittleExprParser.ProgramContext):
        print("\n".join(self.printSymbolTable))
        pass

	# Enter a parse tree produced by LittleExprParser#func_decl.
    def enterFunc_decl(self, ctx:LittleExprParser.Func_declContext):
       self.printSymbolTable.append("\nSymbol table {0}\r".format(ctx.getChild(2).getText()))
       self.symbolTable.append({})
       pass

	# Exit a parse tree produced by LittleExprParser#func_decl.
    def exitFunc_decl(self, ctx:LittleExprParser.Func_declContext):
       pass

	# Enter a parse tree produced by LittleExprParser#if_stmt.
    def enterIf_stmt(self, ctx:LittleExprParser.If_stmtContext):
        self.printSymbolTable.append("\nSymbol table BLOCK {0}\r".format(self.block))
        self.block += 1
        pass

	# Exit a parse tree produced by LittleExprParser#if_stmt.
    def exitIf_stmt(self, ctx:LittleExprParser.If_stmtContext):
        pass

	# Enter a parse tree produced by LittleExprParser#else_part.
    def enterElse_part(self, ctx:LittleExprParser.Else_partContext):
        self.printSymbolTable.append("\nSymbol table BLOCK {0}\r".format(self.block))
        self.symbolTable.append({})
        self.block += 1
        pass

	# Exit a parse tree produced by LittleExprParser#else_part.
    def exitElse_part(self, ctx:LittleExprParser.Else_partContext):
        pass


	# Enter a parse tree produced by LittleExprParser#for_stmt.
    def enterFor_stmt(self, ctx:LittleExprParser.For_stmtContext):
        self.printSymbolTable.append("\nSymbol table BLOCK {0}\r".format(self.block))
        self.symbolTable.append({})
        self.block += 1
        pass

	# Exit a parse tree produced by LittleExprParser#for_stmt.
    def exitFor_stmt(self, ctx:LittleExprParser.For_stmtContext):
        pass

    # Enter a parse tree produced by LittleExprParser#param_decl_list.
    def enterDecl(self, ctx:LittleExprParser.Param_decl_listContext):
        pass

	# Enter a parse tree produced by LittleExprParser#param_decl_list.
    def enterString_decl(self, ctx:LittleExprParser.Param_decl_listContext):
        identifier = ctx.getChild(1).getText()
        value = ctx.getChild(3).getText()
        self.addSymbolToTable(identifier, "STRING", value)
        self.printSymbolTable.append("name {0} type STRING value {1}\r".format(identifier, value))
        pass

	# Exit a parse tree produced by LittleExprParser#param_decl_list.
    def exitString_decl(self, ctx:LittleExprParser.Param_decl_listContext):
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

    # Exit a parse tree produced by LittleExprParser#param_decl_list.
    def exitVar_decl(self, ctx:LittleExprParser.Param_decl_listContext):
        pass

    # Enter a parse tree produced by LittleExprParser#param_decl_list.
    def enterParam_decl(self, ctx:LittleExprParser.Param_decl_listContext):
        varType = ctx.getChild(0).getText()

        #id_list: identifier id_tail ;
        #id_tail: COMMA identifier id_tail | ;

        identifier = ctx.getChild(1)
        self.addSymbolToTable(identifier, varType)
        self.printSymbolTable.append("name {0} type {1}\r".format(identifier.getChild(0).getText(),varType))

        # idTailTree = idListTree.getChild(1)        
        # while(idTailTree.getChildCount() != 0):
        #     print("name {0} type {1}\r".format(idTailTree.getChild(1).getText(),varType))
        #     idTailTree = idTailTree.getChild(2)
        # pass

    # Exit a parse tree produced by LittleExprParser#param_decl_list.
    def exitParam_decl(self, ctx:LittleExprParser.Param_decl_listContext):
        pass

    # # Checks if identifier exists in table
    # def checkTable(self, identifier):
    #     if(identifier in self.symbolTable[-1]):
    #         raise SyntaxError(identifier) 

    # Add variable to identifier
    def addSymbolToTable(self, identifier, varType, value=None):
        if(identifier in self.symbolTable[-1]):
            raise SyntaxError(identifier) 
        self.symbolTable[-1][identifier] = (varType, value)