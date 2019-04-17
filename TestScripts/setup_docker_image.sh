#!/bin/bash
set -e

volume_name=trik-checker-sandbox

function prepare_docker_image {
    echo "Downloading and setting up a docker image..."
    sudo docker build -t checker https://github.com/anastasiia-kornilova/epicbox-images.git#xenial:/epicbox-trik -f Dockerfile.xenial

    sudo docker volume create "$volume_name"
    volume_path=$(sudo docker volume inspect $volume_name --format '{{.Mountpoint}}')
    
    echo "Downloading checker rig..."
    sudo svn checkout https://github.com/ibalashov24/semester_4_coursework/branches/mapGenerator/MapGenerator $volume_path/MapGenerator
    sudo svn checkout https://github.com/ibalashov24/semester_4_coursework/branches/travis-integration/TestScripts $volume_path/TestScripts

    sudo cp -a "$volume_path/MapGenerator/." "$volume_path"
    sudo cp -a "$volume_path/TestScripts/." "$volume_path"
    
    echo "Preparing user solution file..."
    sudo cp ./solution.js $volume_path/solution.js
}

function run_testing {
    command="bash /trikStudio-checker/launch_scripts/start_testing.sh"
    
    echo "Launching Docker container"
    sudo docker run -i --name trik-checker -v $volume_name:/trikStudio-checker/launch_scripts checker $command
}

prepare_docker_image
run_testing