import os
import json
from pathlib import Path


class colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Utility:
    APIURL = "https://tinytest.herokuapp.com/api/"

    SCRIPTPATH = str(Path(__file__).parents[1])

    TESTCASESPATH = SCRIPTPATH + "/testcases/step6/input"
    GOLDCOMPILERPATH = SCRIPTPATH + "/goldCompilers/step7/step7.jar"
    ANTLRPATH = SCRIPTPATH + "/goldCompilers/antlr.jar"
    TINYPATH = SCRIPTPATH + "/tiny"
    TINYSOURCEPATH = SCRIPTPATH + "/tiny4Regs.C"
    CONFIGFILE = SCRIPTPATH + "/config.json"
    BASEOUTPUTDIR = SCRIPTPATH + "/output/"
    BASELOGDIR = SCRIPTPATH + "/logs/"

    COMPILEROUTPUT = BASEOUTPUTDIR + "compiledOutput/"
    TINYOUTPUT = BASEOUTPUTDIR + "tinyOutput/"

    GOLDCOMPILEROUTPUT = COMPILEROUTPUT + "gold/"
    ACTUALCOMPILEROUTPUT = COMPILEROUTPUT + "actual/"

    GOLDTINYOUTPUT = TINYOUTPUT + "gold/"
    ACTUALTINYOUTPUT = TINYOUTPUT + "actual/"
    STEPS = ["4", "5", "6"]
    CURRSTEP = "6"

    CONFIGKEYS = ["java", "display", "verbose"]
    POSSIBLEDISPLAYOPTIONS = ["diff", "info", "all"]

    def getConfigData():
        config_file_obj = open(Utility.CONFIGFILE)
        config_string = config_file_obj.read()
        config_dict = json.loads(config_string)

        for configKey in Utility.CONFIGKEYS:
            if configKey not in config_dict.keys():
                raise Exception(
                    ("ERROR! Missing key in config.json file: {0}".format(configKey)))

        config_dict["java"] = int(config_dict["java"])
        config_dict["verbose"] = int(config_dict["verbose"])
        if config_dict["display"] not in Utility.POSSIBLEDISPLAYOPTIONS:
            raise Exception(("Invalid value for display: {0}. Only the following strings are allowed: {1}".format(
                config_dict["display"], ", ".join(Utility.POSSIBLEDISPLAYOPTIONS))))

        return config_dict
