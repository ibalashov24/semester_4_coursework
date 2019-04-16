# -*- coding: utf-8 -*-
import os
import os.path
import json
import shutil
import sys

from uuid import uuid1
from subprocess import run

import generator_import as MapGenerator

class SolutionTester():
    CHECKER_PATH = '/trikStudio-checker/bin/check-solution.sh'
    DEST_FIELD_PATH = '/trikStudio-checker/fields/randomizer'
    SOLUTION_FILE_NAME = '/trikStudio-checker/bin/lastSavedCode.js'
    PROJECT_FILE_NAME = '/trikStudio-checker/examples/randomizer.qrs'
    REPORT_FILE_PATH = './reports/randomizer'
    FIELD_GENERATOR_PATH = '/trikStudio-checker/launch_scripts/generator.py'
    
    FIELD_SET_NUMBER = 10
    
    def __init__(self):
        self.test_number = self.FIELD_SET_NUMBER
        
    def _clean_directory(self, path):
       '''
       Removes all files from given directory
       '''
        
       shutil.rmtree(path, ignore_errors=True)
       os.makedirs(path)
    
    def _generate_fields(self):
        '''
        Generates field sets for the checker
        '''
        
        print("Generating fields...")
        
        self._clean_directory(self.DEST_FIELD_PATH)
        
        for i in range(self.FIELD_SET_NUMBER):
            print("Generating test set ", i)
                    
            generator = MapGenerator.MapGenerator()
            wrapper = MapGenerator.TRIKMapWrapper()
        
            for wall in generator.get_walls():
                wrapper.add_wall(wall[0], wall[1])
        
            point = next(generator.get_new_start_point())
            wrapper.set_start_point((point[0], point[1]), point[2])
            
            wrapper.save_world("{0}/{1}.xml".format(self.DEST_FIELD_PATH, uuid1()))
             
    def _run_checker(self):
        ''' 
        Runs trikStudio-checker process
        '''
        
        self._generate_fields()
        
        print("Running checker: ", file=sys.stderr)
        run([self.CHECKER_PATH,  
             self.PROJECT_FILE_NAME,
             self.SOLUTION_FILE_NAME])
        
    def _interpret_results(self):
        '''
        Reads checker reports and counts the number of successful tests
        '''
        
        print("Interpreting test results...")
        successful_tests = 0
        
        all_reports = os.listdir(self.REPORT_FILE_PATH)
        for report in all_reports:
            print("Interpreting {0}".format(report))
            if (report == "_randomizer"):
                continue
            
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

        self._run_checker()
        return self._interpret_results()
    

tester = SolutionTester()
successful_tests = tester.run()

print("Total tests: ", tester.test_number)
print("Successful: ", successful_tests)

if (tester.test_number != successful_tests):
    exit(1)