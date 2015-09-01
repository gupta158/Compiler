__author__ = 'gupta158, jalliger'

import sys
from antlr4 import *
from antlr4.InputStream import InputStream
from LittleExprLexer import LittleExprLexer
from LittleExprParser import LittleExprParser

if __name__ == '__main__':
    if len(sys.argv) > 1:
        input_stream = FileStream(sys.argv[1])
    else:
        input_stream = InputStream(sys.stdin.readline())

    lexer = LittleExprLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = LittleExprParser(token_stream)
    tree = parser.prog()

    lisp_tree_str = tree.toStringTree(recog=parser)
    print(lisp_tree_str)