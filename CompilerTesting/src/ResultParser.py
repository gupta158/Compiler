import datetime
import subprocess
import os
import re
import time


class ResultParser():

    def __init__(self):
        self.logs = {}  # dictionary of dictionaries {input file: {'commit id':commit_id,'result',result ...}}

    def getTinyOutput(self, input_file, path="CompilerTesting/output/tinyOutput/actual/"):
        return open(os.path.join(path, input_file.replace(".micro", ".out"))).read()

    def parse_results(self, input_files):
        def get_commit_id():
            return subprocess.getoutput("git --git-dir='../.git/' log | head -n1 | cut -d' ' -f2")

        def get_timestamp():
            return datetime.datetime.now().strftime("%m %d %y %H %M %S")
            # return time.time()

        def get_result(tiny_output):
            return tiny_output[0]

        def get_cycles(tiny_output):
            return re.findall(r'Total Cycles = (\d*)', tiny_output)[0]

        def get_instructions(tiny_output):
            return re.findall(r'Instructions:(\d*)', tiny_output)[0]

        def get_reg_mem_used(tiny_output):
            return re.findall(r'Memory Usage \(mem:(\d*),reg:(\d*)\)', tiny_output)[0]

        def parse_error_info(input_file):
            pass
            # stderr should be redirected somewhere that this method will parse for info
            # return error_info

        # commit_id = get_commit_id()
        timestamp = get_timestamp()

        for f in input_files:
            tmp = {}
            tmp['timestamp'] = timestamp
            # tmp['commit_id'] = commit_id

            tiny_output = self.getTinyOutput(f)

            # print(f)
            # print('tiny out')
            # print(tiny_output)
            # print('~~~~~~~~')
            mem_used, reg_used = get_reg_mem_used(tiny_output)

            tmp['result'] = get_result(tiny_output)
            tmp['cycles'] = get_cycles(tiny_output)
            tmp['instructions'] = get_instructions(tiny_output)
            tmp['registers_used'] = reg_used
            tmp['memory_used'] = mem_used
            # tmp['error_info'] = parse_error_info(f)

            self.logs[f] = tmp
