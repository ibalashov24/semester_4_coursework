#!/bin/bash

function build_docker_image {
    echo "Setting up docker image"
    docker build https://github.com/anastasiia-kornilova/epicbox-images.git#xenial:/epicbox-trik -f Dockerfile.xenial --label checker
    docker volume create trik-checker-sandbox
    volume_path=$(docker volume inspect trik-checker-sandbox --format '{{.Mountpoint}}')
    
    echo "Setting up checker stuff"
    svn checkout https://github.com/ibalashov24/semester_4_coursework/trunk/MapGenerator $volume_path
    svn checkout https://github.com/ibalashov24/semester_4_coursework/trunk/TestScripts $volume_path
    
    echo "Copying problem solution"
    cp ./solution.js $volume_path/solution.js
    
    echo "Launching Docker container"
    docker run checker:latest --name trik-checker -v trik-checker-sandbox:/trikStudio-checker/ 'apt update && apt install python3 -y'
    docker run checker:latest --name trik-checker -v trik-checker-sandbox:/trikStudio-checker/ 'cd trikStudio-checker && python3 solution_tester.py'
}

build_docker_image