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
        #input_stream = InputStream(sys.stdin.readline())

    #print("before Lexer!")
    lexer = LittleExprLexer(input_stream)
    #print("before token stream!")
    # for i in lexer.symbolicNames:
    #     print(i)
    token_stream = CommonTokenStream(lexer)
    #print("before token stream get text!")
    # for i in token_stream.getTokens(0, 5000):
    #     print(i)
    printTokens(lexer, token_stream)
    #print("before parsing")
    #parser = LittleExprParser(token_stream)    
    #tree = parser.keyword()

    #lisp_tree_str = tree.toStringTree(recog=parser)
    #print(lisp_tree_str)


def printTokens(lexer, token_stream):
    token_stream.getText()
    for token in token_stream.tokens:
        if( token.type != -1):
            
            print("Token Type: {}".format(lexer.symbolicNames[token.type]))
            print("Value: {}".format(token.text))
        


if __name__ == '__main__':
    main(sys.argv)
