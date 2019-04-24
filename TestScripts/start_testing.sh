#!/bin/bash
set -euo pipefail

# Cleaning example tester fields and movings user's own fields instead (if exists)
new_fields="/trikStudio-checker/launch_scripts/custom_fields"
checker_fields="/trikStudio-checker/fields/randomizer"

rm -rf "${checker_fields:-}"/*

if  [ -d $new_fields ] && ! [ "$(find $new_fields -not -path '*/\.*' -type f | wc -l)" -eq 0 ] ; then
    echo "User fields detected!"
    for open_map in $new_fields/*; do
	file_name=$(basename $open_map)
	cp $open_map $checker_fields/"${file_name%.*}_open.xml"
    done
else
    echo "Fields not found!!! Stopping test proccess"
    exit 1
fi

# Downloading closed fields from referee repo
closed_maps_repo="https://github.com/ibalashov24/closed_maps_4_coursework.git"
git clone $closed_maps_repo ./closed_maps
for map in $(pwd)/closed_maps/closed_fields/*; do
    file_name=$(basename $map)
    cp "$map" $checker_fields/"${file_name%.*}_closed.xml"
done

# Generating some service files for the checker
touch $checker_fields/"no-check-self"
touch $checker_fields/"runmode"

for i in $checker_fields/*.xml; do
    touch "${i%.*}.txt"
done

checker_path="/trikStudio-checker/bin/check-solution.sh"
project_file="/trikStudio-checker/examples/randomizer.qrs"
solution_file="/trikStudio-checker/launch_scripts/solution.js"

echo "Running checker..."
cd "/trikStudio-checker/launch_scripts"
sh -c "$checker_path $project_file $solution_file"
exec

