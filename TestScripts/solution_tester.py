# -*- coding: utf-8 -*-
import os
import json
import shutil
from subprocess import run

class SolutionTester():
    CHECKER_PATH = '/trikStudio-checker/bin/check-solution.sh'
    DEST_FIELD_PATH = '/trikStudio-checker/fields/randomizer'
    SOLUTION_FILE_NAME = '/trikStudio-checker/launch_scripts/solution.js'
    PROJECT_FILE_NAME = '/trikStudio-checker/examples/randomizer.qrs'
    REPORT_FILE_PATH = './reports/randomizer'

    def _run_checker(self):
        ''' 
        Runs trikStudio-checker process
        '''
        
        print("Running checker: ")
        run([self.CHECKER_PATH,  
             self.PROJECT_FILE_NAME,
             self.SOLUTION_FILE_NAME])
        
    def _interpret_results(self):
        '''
        Reads checker reports and counts the number of successful tests
        '''
        
        print("Interpreting test results...")
        successful_tests = 0
        test_number = 0
        
        all_reports = os.listdir(self.REPORT_FILE_PATH)
        for report in all_reports:
            print("Interpreting {0}".format(report))
            if (report == "_randomizer"):
                continue

	    test_number += 1
            
            report_file = open(self.REPORT_FILE_PATH + "/" + report, "r")
            report_deserialized = json.load(report_file)[0]
        
            print("Field {0}; Status: {1}".format(report, report_deserialized["message"]))
            if (report_deserialized["message"] == "Задание выполнено!"):
                successful_tests += 1
                
            report_file.close()
        
        return successful_tests
    
    def run(self):
        '''
        Runs test procedure
        '''
        
        print("Beginning test process...")
    
        self._run_checker()
        return self._interpret_results()
    

tester = SolutionTester()
test_number, successful_tests = tester.run()

print("Total tests: ", test_number)
print("Successful: ", successful_tests)

if (test_number != successful_tests):
    exit(1)