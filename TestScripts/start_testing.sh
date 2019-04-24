#!/bin/bash
set -euo pipefail

# Cleaning example tester fields and movings user's own fields instead (if exists)
new_fields="/trikStudio-checker/launch_scripts/custom_fields"
checker_fields="/trikStudio-checker/fields/randomizer"

rm -rf "${checker_fields:-}/*"

if  [ -d $new_fields ] && ! [ "$(find $new_fields -not -path '*/\.*' -type f | wc -l)" -eq 0 ] ; then
    echo "User fields detected!"
    cp -r $new_fields/. $checker_fields
else
    echo "Fields not found!!! Stopping test proccess"
    exit 1
fi

# Generating some service files for the checker
touch $checker_fields/"no-check-self"
touch $checker_fields/"runmode"

for i in $checker_fields; do
    if [[ $i != *.xml ]]; then
	continue
    fi
    
    touch $checker_fields/"${i%.*}.txt"
done

checker_path="/trikStudio-checker/bin/check-solution.sh"
project_file="/trikStudio-checker/examples/randomizer.qrs"
solution_file="/trikStudio-checker/launch_scripts/solution.js"

cd "/trikStudio-checker/launch_scripts"
bash -c "$checker_path $project_file $solution_file"
exec

# Running checking proccess
#exec python3 /trikStudio-checker/solution_tester.py