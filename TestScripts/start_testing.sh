#/bin/bash

apt update
apt install python3 -y

# Cleaning example tester fields and movings user's own fields instead (if exists)
new_fields="/trikStudio-checker/launch_scripts/custom_fields"
checker_fields="/trikStudio-checker/fields/randomizer"

rm -rf $checker_fields/*

if  [ -d $new_fields ] && ! [ `ls $new_fields | wc -l` -eq 0 ] ; then
    echo "User fields detected!"
    cp -r $new_fields/. $checker_fields
else
    echo "Fields not found!!! Stopping test proccess"
    exit 1
fi

# Running checking proccess
python3 /trikStudio-checker/launch_scripts/solution_tester.py