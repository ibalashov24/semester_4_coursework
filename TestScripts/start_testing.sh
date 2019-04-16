#/bin/bash

apt update
apt install python3 -y

cd trikStudio-checker
python3 solution_tester.py