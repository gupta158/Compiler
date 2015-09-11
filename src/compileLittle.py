__author__ = 'gupta158, jalliger'

import sys
from antlr4 import *
from antlr4.InputStream import InputStream
from LittleExprLexer import LittleExprLexer
from LittleExprParser import LittleExprParser
from LittleExprErrorStrategy import LittleExprErrorStrategy


def main(argv):
    if len(argv) > 1:
        input_stream = FileStream(argv[1])
    else:
        print("ERROR!, no file provided")
        return

    lexer = LittleExprLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    #printTokens(lexer, token_stream)

    parser = LittleExprParser(token_stream)  
    errorHandler = LittleExprErrorStrategy()
    parser._errHandler = errorHandler
    
    
    try:
        tree = parser.program()
        print("Accepted")
        lisp_tree_str = tree.toStringTree(recog=parser)
    except:
        print("Not accepted")
    
     #   print("Not accepted")
    #else:
    #    print("Accepted")


   
    #print(lisp_tree_str)

    # for child in tree.getChildren():
    #     print(child.getText())
    #     print("HGEY")

def printTokens(lexer, token_stream):
    token_stream.getText()
    for token in token_stream.tokens:
        if( token.type != -1):    
            print("Token Type: {}".format(lexer.symbolicNames[token.type]))
            print("Value: {}".format(token.text))
        


if __name__ == '__main__':
    main(sys.argv)
