import datetime
import subprocess
import os
import re
import time
import json
import requests

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
        print(jsonPost)
        client = requests.session()

        # Retrieve the CSRF token first
        url = "https://tinytest.herokuapp.com/api/"        
        #client.get(url)  # sets cookie
        #csrftoken = client.cookies['csrf']
        #data_json = json.dumps(jsonPost)
        headers = {'Content-Type': 'application/json'}
        r = requests.post(url, data=json.dumps(jsonPost), headers=headers)
        print(r)
        print(json.dumps(r.json(), indent=4))
        return