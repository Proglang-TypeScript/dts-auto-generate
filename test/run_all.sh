#! /usr/bin/env bash

set -euo pipefail

TESTMOD="../testmodules"
RTI="/rti"

trap 'exit 1' SIGINT

function process() {
	name=$1
	dir="$TESTMOD/$name"
	echo "$name: $dir"
	timeout -k 2 4 "$RTI/bin/runNew" "$dir" "$name" || {
		code=$?
		if [ $code -eq 124 ]; then
			echo "timeout"
		else
			exit 1	
		fi
	}
	echo
}

if [[ -z "${1+x}" ]]; then
	while read name; do
		process "$name"
	done < "../works.txt"
else
	process "$1"
fi

