#! /usr/bin/env bash

set -euo pipefail

IMGNAME=find1

if ! sudo docker image inspect $IMGNAME > /dev/null; then
	pushd docker
	sudo docker build -t $IMGNAME .
	popd
fi

sudo docker run --rm -it -v $(pwd -P):/app $IMGNAME
