import datetime
import subprocess
import os
import re
import time
import json
import urllib.request

from Utility import *

class JSONPostResults():
    def __init__(self, userName, currentDate):
        self.userName    = userName
        self.currentDate = currentDate
        self.tests = {}

    def addTest(self, fileName, cycles, instr, regUsed):
        self.tests[fileName] = {
                                "cycles"        : cycles,
                                "instructions"  : instr,
                                "registers"     : regUsed
                              }

    def post(self):
        jsonPost = {
                        "name"    : self.userName,
                        "datetime": self.currentDate,
                        "tests"   : self.tests  
                    }
               
        headers = {'Content-Type': 'application/json'}
        req = urllib.request.Request(Utility.APIURL, data=json.dumps(jsonPost).encode('utf8'), headers=headers)
        response = urllib.request.urlopen(req)
        responseStr = (response.read().decode('utf8'))
        if responseStr != "noice":
            print(colors.RED +  "FAILED to post data" + colors.ENDC)
        return