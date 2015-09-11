# Generated from LittleExpr.g4 by ANTLR 4.5.1
# encoding: utf-8
from antlr4 import *
from antlr4.error.ErrorStrategy import *
from io import StringIO
import sys
import os

class LittleExprErrorStrategy ( DefaultErrorStrategy ):

  errorCount = 0
  def __init__(self):
    super().__init__()

  def reportError(self, recognizer:Parser, e:RecognitionException):
    # if we've already reported an error and have not matched a token
    # yet successfully, don't report any errors.
    self.errorCount = self.errorCount + 1

  def recoverInline(self, recognizer:Parser):
    # if we've already reported an error and have not matched a token
    # yet successfully, don't report any errors.
    stderr = sys.stderr
    sys.stderr = open(os.devnull, 'w')

    super().recoverInline(recognizer)
    sys.stderr = stderr
    self.errorCount = self.errorCount + 1
