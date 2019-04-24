#!/bin/bash
set -euo pipefail

volume_name=trik-checker-sandbox

function prepare_docker_image {
    echo "Downloading and setting up a docker image..."
    docker build -t checker https://github.com/ibalashov24/epicbox-images.git#travis-checker:/epicbox-trik -f Dockerfile.xenial

    docker volume create "$volume_name"
    volume_path=$(sudo docker volume inspect $volume_name --format '{{.Mountpoint}}')
    
    echo "Preparing user solution file..."
    cp ./solution.js "$volume_path"/solution.js
    
    if  [ -d ./test_fields ] && ! [ "$(find ./test_fields -not -path '*/\.*' -type f  | wc -l)" -eq 0 ] ; then
	echo "Preparing user fields..."
	cp -r ./test_fields/. "$volume_path"/custom_fields
    else
	echo "Fields not found in ./test_fields !!!"
	exit 1
    fi
}

function run_testing {
    command="bash /trikStudio-checker/start_testing.sh"
    
    echo "Launching Docker container"
    docker run -i --name trik-checker -v $volume_name:/trikStudio-checker/launch_scripts checker "$command"
}

prepare_docker_image
exec run_testing