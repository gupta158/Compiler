from antlr4 import *
from LittleExprParser import LittleExprParser
from LittleExprListener import LittleExprListener

# This class defines a complete listener for a parse tree produced by LittleExprParser.
class SymbolTableGenerator(LittleExprListener):

    def __init__(self):
        super().__init__()
        self.block = 1

	# Enter a parse tree produced by LittleExprParser#program.
    def enterProgram(self, ctx:LittleExprParser.ProgramContext):
        print("Symbol Table GLOBAL")
        pass

	# Exit a parse tree produced by LittleExprParser#program.
    def exitProgram(self, ctx:LittleExprParser.ProgramContext):
        pass

	# Enter a parse tree produced by LittleExprParser#func_decl.
    def enterFunc_decl(self, ctx:LittleExprParser.Func_declContext):
       print("\nSymbol Table {0}".format(ctx.getChild(2).getText()))
       pass

	# Exit a parse tree produced by LittleExprParser#func_decl.
    def exitFunc_decl(self, ctx:LittleExprParser.Func_declContext):
       pass

	# Enter a parse tree produced by LittleExprParser#if_stmt.
    def enterIf_stmt(self, ctx:LittleExprParser.If_stmtContext):
        print("\nSymbol Table BLOCK {0}".format(self.block))
        self.block += 1
        pass

	# Exit a parse tree produced by LittleExprParser#if_stmt.
    def exitIf_stmt(self, ctx:LittleExprParser.If_stmtContext):
        pass

	# Enter a parse tree produced by LittleExprParser#else_part.
    def enterElse_part(self, ctx:LittleExprParser.Else_partContext):
        print("\nSymbol Table BLOCK {0}".format(self.block))
        self.block += 1
        pass

	# Exit a parse tree produced by LittleExprParser#else_part.
    def exitElse_part(self, ctx:LittleExprParser.Else_partContext):
        pass


	# Enter a parse tree produced by LittleExprParser#for_stmt.
    def enterFor_stmt(self, ctx:LittleExprParser.For_stmtContext):
        print("\nSymbol Table BLOCK {0}".format(self.block))
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
        print("name {0} type STRING value {1}".format(ctx.getChild(1).getText(),ctx.getChild(3).getText()))
        pass

	# Exit a parse tree produced by LittleExprParser#param_decl_list.
    def exitString_decl(self, ctx:LittleExprParser.Param_decl_listContext):
        pass

    # Enter a parse tree produced by LittleExprParser#param_decl_list.
    def enterVar_decl(self, ctx:LittleExprParser.Param_decl_listContext):
        varType = ctx.getChild(0).getText()

        #id_list: identifier id_tail ;
        #id_tail: COMMA identifier id_tail | ;

        idListTree = ctx.getChild(1)
        print("name {0} type {1}".format(idListTree.getChild(0).getText(),varType))

        idTailTree = idListTree.getChild(1)        
        while(idTailTree.getChildCount() != 0):
            print("name {0} type {1}".format(idTailTree.getChild(1).getText(),varType))
            idTailTree = idTailTree.getChild(2)
        pass

    # Exit a parse tree produced by LittleExprParser#param_decl_list.
    def exitVar_decl(self, ctx:LittleExprParser.Param_decl_listContext):
        pass

