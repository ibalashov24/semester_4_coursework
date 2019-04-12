# -*- coding: utf-8 -*-
import os
import os.path
import json
import shutil
import sys

from uuid import uuid1
from subprocess import run

class SolutionTester():
    CHECKER_PATH = './bin/check-solution.sh'
    DEST_FIELD_PATH = './fields/randomizer'
    TEST_FOLDER_NAME = './test_sets'
    SOLUTION_FILE_NAME = './bin/lastSavedCode.js'
    PROJECT_FILE_NAME = './examples/randomizer.qrs'
    REPORT_FILE_PATH = './reports/randomizer'
    
    def __init__(self):
        self.test_number = 0

    def _clean_directory(self, path):
        shutil.rmtree(path, ignore_errors=True)
        os.makedirs(path)
    
    def prepare_fields(self):
        '''
        Prepares fields (changes names, locations) for trikStudion-checker
        '''
        
        print("Preparing test fields...", file=sys.stderr)

        # Removing default fields
        self._clean_directory(self.DEST_FIELD_PATH)

        print("Moving fields...", file=sys.stderr)

        # List of all directories with test sets 
        all_dirs = os.listdir(self.TEST_FOLDER_NAME)
        for directory in all_dirs:
            print("Opening {0}".format(directory), file=sys.stderr)
            dir_path = self.TEST_FOLDER_NAME + "/" + directory
            fields = os.listdir(dir_path)
            
            for item in fields:
                self.test_number += 1
                
                # Renaming with unique name in order to avoid collisions between test sets
                shutil.copyfile(
                    dir_path + "/" + item, 
                    '{0}/{1}.xml'.format(self.DEST_FIELD_PATH, uuid1()))

        print("Prepared {0} field".format(self.test_number), file=sys.stderr)
                
 
    def _run_checker(self):
        ''' 
        Runs trikStudio-checker process
        '''
        
        print("Running checker: ", file=sys.stderr)
        run([self.CHECKER_PATH,  
             self.PROJECT_FILE_NAME,
             self.SOLUTION_FILE_NAME])
        
    def _interpret_results(self):
        '''
        Reads checker reports and counts the number of successful tests
        '''
        
        print("Interpreting test results...", file=sys.stderr)
        successful_tests = 0
        
        all_reports = os.listdir(self.REPORT_FILE_PATH)
        for report in all_reports:
            print("Interpreting {0}".format(report))
            if (report == "_randomizer"):
                continue
            
            report_file = open(self.REPORT_FILE_PATH + "/" + report, "r")
            report_deserialized = json.load(report_file)[0]
        
            print("Field {0}; Status: {1}".format(report, report_deserialized["message"]), file=sys.stderr)
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

print("Total tests: ", tester.test_number)
print("Successful: ", successful_tests)