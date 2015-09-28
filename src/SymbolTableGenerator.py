from antlr4 import *
from LittleExprParser import LittleExprParser
from LittleExprListener import LittleExprListener

# This class defines a complete listener for a parse tree produced by LittleExprParser.
class SymbolTableGenerator(LittleExprListener):

	# Enter a parse tree produced by LittleExprParser#program.
    def enterProgram(self, ctx:LittleExprParser.ProgramContext):
        print("Symbol Table GLOBAL")
        pass

	# Exit a parse tree produced by LittleExprParser#program.
    def exitProgram(self, ctx:LittleExprParser.ProgramContext):
        pass

	# Enter a parse tree produced by LittleExprParser#func_decl.
    def enterFunc_decl(self, ctx:LittleExprParser.Func_declContext):
       print("Symbol Table ")
       #print(ctx.func_decl())
       pass

	# Exit a parse tree produced by LittleExprParser#func_decl.
    def exitFunc_decl(self, ctx:LittleExprParser.Func_declContext):
       pass

	# Enter a parse tree produced by LittleExprParser#if_stmt.
    def enterIf_stmt(self, ctx:LittleExprParser.If_stmtContext):
        pass

	# Exit a parse tree produced by LittleExprParser#if_stmt.
    def exitIf_stmt(self, ctx:LittleExprParser.If_stmtContext):
        pass

	# Enter a parse tree produced by LittleExprParser#else_part.
    def enterElse_part(self, ctx:LittleExprParser.Else_partContext):
        pass

	# Exit a parse tree produced by LittleExprParser#else_part.
    def exitElse_part(self, ctx:LittleExprParser.Else_partContext):
        pass


	# Enter a parse tree produced by LittleExprParser#for_stmt.
    def enterFor_stmt(self, ctx:LittleExprParser.For_stmtContext):
        pass

	# Exit a parse tree produced by LittleExprParser#for_stmt.
    def exitFor_stmt(self, ctx:LittleExprParser.For_stmtContext):
        pass

	# Enter a parse tree produced by LittleExprParser#param_decl_list.
    def enterParam_decl_list(self, ctx:LittleExprParser.Param_decl_listContext):
        pass

	# Exit a parse tree produced by LittleExprParser#param_decl_list.
    def exitParam_decl_list(self, ctx:LittleExprParser.Param_decl_listContext):
        pass
