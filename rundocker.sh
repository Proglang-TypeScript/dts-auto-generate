#! /usr/bin/env bash

set -euo pipefail

SCRIPT_PATH="$( cd "$(dirname "$0")" ; pwd -P )"

IMGNAME=dts-auto-generate

if ! sudo docker image inspect $IMGNAME > /dev/null; then
	pushd $SCRIPT_PATH/docker
	sudo docker build -t $IMGNAME .
	popd
fi

exec sudo docker run --rm -it -v $(pwd -P):/app $IMGNAME $@
