#!/bin/bash

IMAGE_NAME="ollama_chat.py"

XAUTH_FILE="/tmp/.docker.xauth"
touch $XAUTH_FILE
chmod 777 $XAUTH_FILE

xauth nlist $DISPLAY | sed -e 's/^..../ffff/' | xauth -f $XAUTH_FILE nmerge -

sudo docker run -it --rm \
  --net=host \
  -e DISPLAY=$DISPLAY \
  -e XAUTHORITY=$XAUTH_FILE \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v $XAUTH_FILE:$XAUTH_FILE \
  $IMAGE_NAME

rm -f $XAUTH_FILE
