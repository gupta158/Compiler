import csv
import getpass
import os.path
from pprint import pprint as pp
from src.Utility import Utility


class TestLogger():
    def __init__(self, file_name):
        self.file_name = file_name
        self.log_name = getpass.getuser() + '-' + self.file_name + '-log.csv'
        self.logs = []

    def add_entry_to_log(self, entry_dict):
        already_existed = os.path.isfile(os.path.join(Utility.BASELOGDIR, self.log_name))

        with open(os.path.join(Utility.BASELOGDIR, self.log_name), 'a') as csvfile:
            fieldnames = ['timestamp', 'commit_id', 'result', 'cycles', 'instructions', 'registers_used', 'memory_used', 'error_info']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if not already_existed:
                writer.writeheader()
            writer.writerow(entry_dict)

    def get_previous_entry(self):
        pass

    def calculate_difference(self, other_entry):
        # calculates how cycles, instr, registers have changed since last test
        pass

    def get_full_log(self):
        with open(os.path.join(Utility.BASELOGDIR, self.log_name), 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for r in reader:
                self.logs.append(r)

