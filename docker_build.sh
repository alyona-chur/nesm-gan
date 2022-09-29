#!/bin/bash

# Parse input parameters
IMAGE_TYPE="cpu"
while getopts ":d:t:i:m:" opt; do
  case $opt in
    t) image_type="$OPTARG"
      if [ "$docker_image_type" != "" ]; then
        IMAGE_TYPE="$image_type"
      fi
    ;;
    \?) echo "Invalid option -$OPTARG" >&2;;
  esac
done

if [ "$IMAGE_TYPE" == "gpu" ]; then
  IMAGE_NAME='nes-gan-gpu'
  DOCKERFILE_PATH='docker/gpu.Dockerfile'
elif [ "$IMAGE_TYPE" == "cpu" ]; then
  IMAGE_NAME='nes-gan-cpu'
  DOCKERFILE_PATH='docker/cpu.Dockerfile'
else
  echo "Unable to build docker image, unknown image type $IMAGE_TYPE";
  exit 1
fi

cmd="docker build "
cmd+="--build-arg USER_NAME=$(whoami) "
cmd+="--build-arg USER_ID=$(id -u ${USER}) "
cmd+="--build-arg GROUP_ID=$(id -g ${USER}) "
cmd+="-t ${IMAGE_NAME}-${USER} "
cmd+="-f ${DOCKERFILE_PATH} "
cmd+="."

echo "$cmd"
eval "$cmd"
