#!/bin/bash

function build_docker_image {
    # Setting up docker image
    echo "docker build https://github.com/anastasiia-kornilova/epicbox-images.git#xenial:/epicbox-trik -f Dockerfile.xenial --label checker"
    echo "docker volume create trik-checker-sandbox"
    volume_path=$(docker volume inspect trik-checker-sandbox --format '{{.Mountpoint}}')
    
    # Setting up checker stuff
    echo "svn checkout https://github.com/ibalashov24/semester_4_coursework/trunk/MapGenerator $volume_path"
    echo "svn checkout https://github.com/ibalashov24/semester_4_coursework/trunk/TestScripts $volume_path"
    
    # Copying problem solution
    echo "cp ./solution.js $volume_path/solution.js"
    
    # Launching Docker container
    echo "docker run checker:latest --name trik-checker -v trik-checker-sandbox:/trikStudio-checker/ 'apt update && apt install python3 -y'"
    echo "docker run checker:latest --name trik-checker -v trik-checker-sandbox:/trikStudio-checker/ 'cd trikStudio-checker && python3 solution_tester.py'"
}

build_docker_image