__author__ = 'gupta158, jalliger'

import sys
from antlr4 import *
from antlr4.InputStream import InputStream
from LittleExprLexer import LittleExprLexer
from LittleExprParser import LittleExprParser
from LittleExprErrorStrategy import LittleExprErrorStrategy
from SymbolTableGenerator import SymbolTableGenerator


def main(argv):
    if len(argv) > 1:
        input_stream = FileStream(argv[1])
    else:
        print("ERROR!, no file provided")
        return

    lexer = LittleExprLexer(input_stream)
    token_stream = CommonTokenStream(lexer)

    parser = LittleExprParser(token_stream)  
    errorHandler = LittleExprErrorStrategy()
    parser._errHandler = errorHandler
    
    
    try:
        tree = parser.program()
        lisp_tree_str = tree.toStringTree(recog=parser)
    except:
        print("Not accepted\r")
        return

    try:
        printer = SymbolTableGenerator()
        walker = ParseTreeWalker()
        walker.walk(printer, tree)
    except SyntaxError as e:
        print("DECLARATION ERROR {0}\r".format(e))
        return

def printTokens(lexer, token_stream):
    token_stream.getText()
    for token in token_stream.tokens:
        if( token.type != -1):    
            print("Token Type: {}".format(lexer.symbolicNames[token.type]))
            print("Value: {}".format(token.text))
        


if __name__ == '__main__':
    main(sys.argv)
