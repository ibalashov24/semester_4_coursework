#!/bin/bash
set -e

volume_name=trik-checker-sandbox_2

function prepare_docker_image {
    echo "Downloading and setting up a docker image"
#    docker build https://github.com/anastasiia-kornilova/epicbox-images.git#xenial:/epicbox-trik -f Dockerfile.xenial --label checker

    docker volume create "$volume_name"
    volume_path=$(docker volume inspect $volume_name --format '{{.Mountpoint}}')

    echo $volume_path
    
    echo "Downloading checker rig"
    svn checkout https://github.com/ibalashov24/semester_4_coursework/branches/mapGenerator/MapGenerator $volume_path/MapGenerator
    svn checkout https://github.com/ibalashov24/semester_4_coursework/branches/travis-integration/TestScripts $volume_path/TestScripts

    cp -a "$volume_path/MapGenerator/." "$volume_path"
    cp -a "$volume_path/TestScripts/." "$volume_path"
    
    echo "Preparing user solution file"
    cp ./solution.js $volume_path/solution.js
}

function run_testing {
    command="bash /trikStudio-checker/start_testing.sh"
    
    echo "Launching Docker container"
    docker run -i --name trik-checker2 -v $volume_name:/trikStudio-checker/launch_scripts checker:latest $command
}

prepare_docker_image
run_testing