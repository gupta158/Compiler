__author__ = 'gupta158, jalliger'

import sys
from antlr4 import *
from antlr4.InputStream import InputStream
from LittleExprLexer import LittleExprLexer
from LittleExprParser import LittleExprParser

def main(argv):
    if len(argv) > 1:
        input_stream = FileStream(argv[1])
    else:
        print("ERROR!, no file provided")
        return
        
    lexer = LittleExprLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    printTokens(lexer, token_stream)


def printTokens(lexer, token_stream):
    token_stream.getText()
    for token in token_stream.tokens:
        if( token.type != -1):
            
            print("Token Type: {}".format(lexer.symbolicNames[token.type]))
            print("Value: {}".format(token.text))
        


if __name__ == '__main__':
    main(sys.argv)
