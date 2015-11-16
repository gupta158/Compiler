This repo contains the client side code of Compiler Tester. Steps to use this:
  1. Clone this repo into your project directory:
      git clone git@github.com:gupta158/CompilerTesting.git

    This creates a CompilerTesting Folder that contains all the scripts needed to use this tool

  2. Go into the CompilerTesting directory and open the config.json file

    ```
    { 
    "java": "0", 
    "display": "all",
    "verbose": "1"
    }
    ```
    Indicate if you are using Java by entering a "1" in that field. If you are using C++ or any other language, set it to "0".
    Display has 3 options: 'all', 'info', 'diff'. Info prints out the cycles, instructions and registers used, diff prints out the diff if it fails and all prints both of these things. 
    Indicate if you want to have information printed to screen as the script is run ("1" or "0")

  3. To run the script, go back to the main project directory (i.e. your compiler directory) the following commands are your options:
    
    a. This runs all the test cases for the currentstep

            python3 CompilerTesting/TinyTest.py
          
    b.  This runs all the test cases for all steps after and including step4
    
           python3 CompilerTesting/TinyTest.py --step all
           
    c.  This runs all the test cases for a certain step, either 4 or 5
  
           python3 CompilerTesting/TinyTest.py --step 4  
           
    d.  This runs a certain testcase of the current step, to run a test of a different step add the --step
    
            python3 CompilerTesting/TinyTest.py --test test_expr.micro
    
          

  4. The output will tell you whether you passed or failed the testcases, if all passed then the data will be posted to the site. You can look at the output folder to see what was generated.
      output/CompiledOutput -> The tiny that is generated for the testcases
      output/CompiledOutput -> The output of the testcase using tiny

