import sys
DEFAULTTESTPATH = '../testcases/input'
TESTFILE = "runTestOutput"

def runAllTests(dirPath = None):
	if dirPath is None:
		dirPath = DEFAULTTESTPATH
	files = [f for f in os.listdir(dirPath) if path.isfile(f)]
	for fileName in files
    	runProc = subprocess.Popen(['./Micro',  fileNames],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    	output, error = runProc.communicate()
    	outFile = file.open(TESTFILE, "w")
    	outFile.write(output)
    	outFile.close()



def main():
	testType = 1
	if len(sys.argv) > 1:
		if sys.argv[2] == "all":
			testType = 2

	if testType == 2:
		if len(sys.argv) > 2:
			runAllTests(sys.argv[2])
		else:
			runAllTests()	

if __name__ == "__main__"
	main()
  

STATISTICS ____