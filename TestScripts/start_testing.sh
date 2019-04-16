#/bin/bash

apt update
apt install python3

cd trikStudio-checker
python3 solution_tester.py &> test_results.txt