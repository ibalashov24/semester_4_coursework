#!/bin/bash
set -e

volume_name=trik-checker-sandbox_2

function prepare_docker_image {
    echo "Downloading and setting up a docker image"
    docker build https://github.com/anastasiia-kornilova/epicbox-images.git#xenial:/epicbox-trik -f Dockerfile.xenial --label checker

    docker volume create "$volume_name"
    volume_path=$(docker volume inspect $volume_name --format '{{.Mountpoint}}')

    echo $volume_path
    
    echo "Downloading checker rig"
    svn checkout https://github.com/ibalashov24/semester_4_coursework/trunk/MapGenerator $volume_path/MapGenerator
    svn checkout https://github.com/ibalashov24/semester_4_coursework/trunk/TestScripts $volume_path/TestScripts

    cp -a "$volume_path/MapGenerator/." "$volume_path"
    cp -a "$volume_path/TestScripts/." "$volume_path"
    
    echo "Preparing user solution file"
    cp ./solution.js $volume_path/solution.js
}

function run_testing {
    command='/bin/bash -c "apt update && apt install python3 -y && cd trikStudio-checker && python3 solution_tester.py"'
    
    echo "Launching Docker container"
    docker run --name trik-checker2 -v "$volume_name":/trikStudio-checker/  checker:latest $command
}

prepare_docker_image
run_testing