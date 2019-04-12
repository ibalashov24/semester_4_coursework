# -*- coding: utf-8 -*-
import os
import os.path
import json

from uuid import uuid1
from shutil import copyfile
from subprocess import run

class SolutionTester():
    CHECKER_PATH = './bin/check-solution.sh'
    DEST_FIELD_PATH = './fields/randomizer'
    TEST_FOLDER_NAME = './test_sets'
    SOLUTION_FILE_NAME = 'solution.js'
    REPORT_FILE_PATH = 'reports/randomizer'
    
    def __init__(self):
        self.test_number = 0    
    
    def prepare_fields(self):
        '''
        Prepares fields (changes names, locations) for trikStudion-checker
        '''
        
        # List of all directories with test sets 
        all_dirs = filter(os.path.isdir, os.listdir(self.TEST_FOLDER_NAME))
        for directory in all_dirs:
            print("Opening {0}".format(directory))
            fields = filter(os.path.isfile, os.listdir(directory))
            
            for item in fields:
                print("Moving {0}".format(item))
                
                self.test_number += 1
                
                # Renaming with unique name in order to avoid collisions between test sets
                copyfile(
                    item, 
                    '{0}/{1}.xml'.format(self.DEST_FIELD_PATH, uuid1()))
                
 
    def _run_checker(self):
        ''' 
        Runs trikStudio-checker process
        '''
        
        print("Running checker: ")
        run([self.CHECKER_PATH, 
            self.DEST_FIELD_PATH, 
            self.SOLUTION_FILE_NAME])
        
    def _interpret_results(self):
        '''
        Reads checker reports and counts the number of successful tests
        '''
        
        print("Interpreting test results...")
        successful_tests = 0
        
        all_reports = filter(os.path.isfile, os.listdir(self.REPORT_FILE_PATH))
        for report in all_reports:
            print("Interpreting {0}".format(report))
            if (report == "_randomizer"):
                continue
            
            report_file = open(report, "r")
            report_deserialized = json.load(report_file)
        
            if (report_deserialized["message"] == "Задание выполнено!"):
                successful_tests += 1
                
            report_file.close()
        
        return successful_tests
    
    def run(self):
        '''
        Runs test procedure
        '''
        
        self._run_checker()
        return self._interpret_results()
    

tester = SolutionTester()
tester.prepare_fields()
successful_tests = tester.run()

print(tester.test_number)
print(successful_tests)