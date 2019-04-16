#!/bin/bash
set -e

function prepare_docker_image {
    echo "Setting up docker image"
    docker build https://github.com/anastasiia-kornilova/epicbox-images.git#xenial:/epicbox-trik -f Dockerfile.xenial --label checker

    docker volume create trik-checker-sandbox_2
    volume_path=$(docker volume inspect trik-checker-sandbox --format '{{.Mountpoint}}')

    echo $volume_path
    
    echo "Setting up checker stuff"
    svn checkout https://github.com/ibalashov24/semester_4_coursework/trunk/MapGenerator $volume_path
    svn checkout https://github.com/ibalashov24/semester_4_coursework/trunk/TestScripts $volume_path
    
    echo "Copying problem solution"
    cp ./solution.js $volume_path/solution.js
}

function run_testing {
    command='apt update && apt install python3 -y && cd trikStudio-checker && python3 solution_tester.py'
    
    echo "Launching Docker container"
    docker run checker:latest --name trik-checker2 -v trik-checker-sandbox_2:/trikStudio-checker/ "$command"
}

prepare_docker_image
run_testing