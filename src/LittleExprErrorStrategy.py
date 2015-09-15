# Generated from LittleExpr.g4 by ANTLR 4.5.1
# encoding: utf-8
from antlr4 import *
from antlr4.error.ErrorStrategy import *
from io import StringIO
import sys
import os

class LittleExprErrorStrategy ( DefaultErrorStrategy ):
  def __init__(self):
    super().__init__()

  def reportError(self, recognizer:Parser, e:RecognitionException):
    # if we've already reported an error and have not matched a token
    # yet successfully, don't report any errors.
    raise SyntaxError("syntax error")

  def recoverInline(self, recognizer:Parser):
    # if we've already reported an error and have not matched a token
    # yet successfully, don't report any errors.
    super().recoverInline(recognizer)
