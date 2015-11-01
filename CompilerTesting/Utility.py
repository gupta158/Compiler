import os
import json

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

	SCRIPTPATH = (os.path.dirname(os.path.realpath(__file__)))
	
	TESTCASESPATH = SCRIPTPATH + "/testcases/step4/input"
	GOLDCOMPILERPATH = SCRIPTPATH + "/goldCompilers/step5/step5.jar"
	ANTLRPATH = SCRIPTPATH + "/goldCompilers/antlr.jar"
	TINYPATH = SCRIPTPATH + "/tiny"
	CONFIGFILE = SCRIPTPATH + "/config.json"
	BASEOUTPUTDIR = SCRIPTPATH + "/output/"
	BASELOGDIR = SCRIPTPATH + "/logs/"

	COMPILEROUTPUT = BASEOUTPUTDIR + "compiledOutput/"
	TINYOUTPUT = BASEOUTPUTDIR + "tinyOutput/"
	
	GOLDCOMPILEROUTPUT = COMPILEROUTPUT + "gold/"
	ACTUALCOMPILEROUTPUT = COMPILEROUTPUT + "actual/"

	GOLDTINYOUTPUT = TINYOUTPUT + "gold/"
	ACTUALTINYOUTPUT = TINYOUTPUT + "actual/"

	def getConfigData():
	    config_file_obj = open(Utility.CONFIGFILE)
	    config_string = config_file_obj.read()
	    config_dict = json.loads(config_string)
	    config_dict["java"] = int(config_dict["java"])
	    return config_dict
