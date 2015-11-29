import sys
import os
import subprocess
import getpass
import datetime
import json
import re

from src.ResultParser import ResultParser
from src.TestLogger import TestLogger
from src.JSONPostResults import JSONPostResults
from pprint import pprint as pp
from src.Utility import *
import argparse

from prettytable import PrettyTable

compiled_code = {}


def log(s, level):
    configData = Utility.getConfigData()
    if configData["verbose"]:  # change to be adapted from config
        print(" " * (level * 2) + str(s))


def compileTiny():
    runProc = subprocess.Popen(
        ["g++", "-w", Utility.TINYSOURCEPATH, "-o",  Utility.TINYPATH])
    runProc.communicate()
    return


def setupDirectoryStructure():
    directoryNames = [Utility.BASELOGDIR, Utility.BASEOUTPUTDIR, Utility.COMPILEROUTPUT, Utility.GOLDCOMPILEROUTPUT,
                      Utility.ACTUALCOMPILEROUTPUT, Utility.TINYOUTPUT, Utility.GOLDTINYOUTPUT, Utility.ACTUALTINYOUTPUT]
    for directoryName in directoryNames:
        if not os.path.isdir(directoryName):
            os.mkdir(directoryName)


def runCompiler(input_file, gold=False):
    configData = Utility.getConfigData()
    if gold:
        args = ['java', '-cp', Utility.ANTLRPATH + ':' + Utility.GOLDCOMPILERPATH,
                'Micro', os.path.join(Utility.TESTCASESPATH, input_file)]
        compiler_output = Utility.GOLDCOMPILEROUTPUT
    else:
        if configData["java"]:
            args = ['java', '-cp', 'lib/antlr.jar:classes/', 'Micro',
                    os.path.join(Utility.TESTCASESPATH, input_file)]
            # pretty sure this is an error but putting a comment to remind
            # manish
            compiler_output = Utility.GOLDCOMPILEROUTPUT  # <-- Actual

        else:
            args = ['./Micro',
                    os.path.join(Utility.TESTCASESPATH, input_file)]
            compiler_output = Utility.ACTUALCOMPILEROUTPUT

    compiled_output = os.path.join(
        compiler_output, input_file.replace(".micro", ".tiny"))
    fp = open(compiled_output, 'w')
    runProc = subprocess.Popen(args, stdout=fp)
    error = runProc.communicate()


def runTiny(input_file, gold=False):
    if gold:
        compiler_output = os.path.join(
            Utility.GOLDCOMPILEROUTPUT, input_file.replace(".micro", ".tiny"))
        tiny_output = open(os.path.join(
            Utility.GOLDTINYOUTPUT, input_file.replace(".micro", ".out")), 'w')
    else:
        compiler_output = os.path.join(
            Utility.ACTUALCOMPILEROUTPUT, input_file.replace(".micro", ".tiny"))
        tiny_output = open(os.path.join(
            Utility.ACTUALTINYOUTPUT, input_file.replace(".micro", ".out")), 'w')

    args = [Utility.TINYPATH, compiler_output]

    if os.path.exists(os.path.join(Utility.TESTCASESPATH, input_file.replace(".micro", ".input"))):
        input_file = open(os.path.join(Utility.TESTCASESPATH,
                                       input_file.replace(".micro", ".input")), 'r')
    else:
        input_file = None

    runProc = subprocess.Popen(
        args, stdout=tiny_output, stdin=input_file, shell=False)
    error = runProc.communicate()


# Runs the compiler against the input_files
def runGoldCompilerAndTiny(input_files):
    for fileName in input_files:
        runCompiler(fileName, gold=True)
        runTiny(fileName, gold=True)
    return


# Run gold compiler and tiny
def runActualCompilerAndTiny(input_files):
    for fileName in input_files:
        log("File: {}".format(fileName), 3)
        log("Compiling {}".format(fileName), 4)
        runCompiler(fileName)
        log("Finished Compiling {}, now executing..".format(fileName), 4)
        runTiny(fileName)
        log("Finished Executing {}".format(fileName), 4)
        log("", 4)


def getTinyOutput(input_file, path=Utility.ACTUALTINYOUTPUT):
    return open(os.path.join(path, input_file.replace(".micro", ".out"))).read()


def compareTinyOutput(input_files):
    passedInputFiles = []
    outputStr = ""
    diffDict = {}
    for fileName in input_files:
        actualOutput = getTinyOutput(fileName).split("STATISTIC")[0]
        goldOutput = getTinyOutput(
            fileName, path=Utility.GOLDTINYOUTPUT).split("STATISTIC")[0]
        if actualOutput == goldOutput:
            outputStr += ("{0}{1:<30}PASSED{2}\n".format(colors.GREEN,
                                                         fileName, colors.ENDC))
            passedInputFiles.append(fileName)
        else:
            outputStr += ("{0}{1:<30}FAILED{2}\n".format(colors.RED,
                                                         fileName, colors.ENDC))
            diffDict[fileName] = [actualOutput, goldOutput]
    return passedInputFiles, outputStr, diffDict


# Gets all the files that are going to be tested
def getFileNames(testName):
    input_files = []
    inputArg = testName
    if inputArg is None:
        input_files = [f for f in os.listdir(Utility.TESTCASESPATH) if os.path.isfile(
            os.path.join(Utility.TESTCASESPATH, f)) and ".micro" in f]
    else:
        input_files.append(inputArg)

    return input_files

# Update step number for all constant params


def updateStepNum(stepNum):
    Utility.TESTCASESPATH = re.sub(
        r'/testcases/step\d/input', "/testcases/step{0}/input".format(str(stepNum)), Utility.TESTCASESPATH)
    # Utility.GOLDCOMPILERPATH = re.sub("/goldCompilers/step\d/step\d.jar",
    #                                   "/goldCompilers/step{0}/step{0}.jar".format(str(stepNum)), Utility.GOLDCOMPILERPATH)


def runTests(stepNum, testName, dictOutput):
    updateStepNum(stepNum)

    input_files = getFileNames(testName)

    # setup directory structure
    setupDirectoryStructure()

    # scripting
    # run .micro and tiny on your file
    log("Testing compiler", 2)
    runActualCompilerAndTiny(input_files)

    # run gold compiler
    runGoldCompilerAndTiny(input_files)

    # compare output
    log("Comparing outputs", 2)
    passedInputFiles, outputStr, diffDict = compareTinyOutput(input_files)
    # inputs to nico / outputs of Manish
    # input_files -- [List of ~~~~~ALL THE FILE NAMES~~~~~~ lol file names or
    # just the one specified]

    # parsing
    # output dictionary {input_file_name : TestLogEntry()}
    result_parser = ResultParser()
    result_parser.parse_results(passedInputFiles)

    # logging
    loggers = []
    lgs = []

    jsonReqDict = JSONPostResults(getpass.getuser().replace(
        ' ', ''), str(datetime.datetime.now()))
    diffString = ""
    infoString = ""

    log("Collecting data", 2)

    for f in passedInputFiles:
        logger = TestLogger(file_name=f)
        logger.add_entry_to_log(result_parser.logs[f])
        loggers.append(logger)
        logger.get_full_log()
        jsonReqDict.addTest(f, result_parser.logs[f]['cycles'], result_parser.logs[f][
                            'instructions'], result_parser.logs[f]['registers_used'])

        dictOutput["info"].add_row([f, result_parser.logs[f]['cycles'], result_parser.logs[f]['instructions'],
                                    result_parser.logs[f]['registers_used'], result_parser.logs[f]['memory_used']])

    for f in input_files:
        if f not in passedInputFiles:
            diffString += " {0}:\n".format(f)
            diffString += "  YOUROUTPUT: \n    {0}".format(diffDict[f][0])
            # would be cool if these were interweaved so that it was error,
            # offending statement, error, offending statement etc.
            error_check = re.findall(r'error on line (\d+)', diffDict[f][0])
            if error_check:
                for line_num in error_check:
                    line_num = int(line_num)
                    compiler_output = Utility.ACTUALCOMPILEROUTPUT
                    compiled_output = os.path.join(
                        compiler_output, f.replace(".micro", ".tiny"))
                    with open(compiled_output, 'r') as fp:
                        tiny_code = fp.readlines()
                        error_line = tiny_code[line_num]
                        diffString += "      {}\n".format(error_line)

            diffString += "  GOLDOUTPUT: \n    {0}".format(diffDict[f][1])

    dictOutput["final"] += outputStr
    dictOutput["diff"] += diffString

    log("", 2)

    if(len(passedInputFiles) == len(input_files)):
        log("Posting to tinytest", 2)
        jsonReqDict.post()
        log("Post completed!", 2)
    else:
        log("Did not pass testcases! Not posting to tinytest", 2)

    log("\n\n", 2)

    return dictOutput


def main():

    parser = argparse.ArgumentParser(description='Run tests for compiler')
    parser.add_argument('--test', metavar='testName', type=str, nargs='?',
                        help='The test name to run (eg. test_expr.micro)')
    parser.add_argument('--step',  metavar='stepNum', type=str, nargs='?',
                        help='The step to run (default is the step due)')

    args = parser.parse_args()
    argsDict = vars(args)
    testName = argsDict['test']
    stepStr = argsDict['step']
    configData = Utility.getConfigData()
    dictOutput = {}
    dictOutput["info"] = PrettyTable(
        ['Test File', 'Cycles', 'Instructions', 'Registers', 'Memory'])
    dictOutput["info"].align['Test File'] = "l"
    dictOutput["info"].align['Cycles'] = "r"
    dictOutput["info"].align['Instructions'] = "r"
    dictOutput["info"].align['Registers'] = "r"
    dictOutput["info"].align['Memory'] = "r"

    dictOutput["diff"] = "DIFF: \n"
    dictOutput["final"] = ""
    steps = []

    compileTiny()

    if stepStr == "all":
        steps = Utility.STEPS
        testName = None
    elif stepStr in Utility.STEPS:
        steps.append(stepStr)
    else:
        steps.append(Utility.CURRSTEP)

    for step in steps:
        log("", 1)
        log("Running Tests for Step {}".format(step), 1)
        dictOutput = runTests(step, testName, dictOutput)

    if configData["display"] in ["diff", "all"]:
        if dictOutput["diff"] != "DIFF: \n":
            print(dictOutput["diff"])

    if configData["display"] in ["info", "all"]:
        log("STATISTICS:", 0)
        print(dictOutput["info"])
        log("\n\n", 1)

    print("==============RESULTS===============")
    print(dictOutput["final"])


if __name__ == '__main__':
    main()
