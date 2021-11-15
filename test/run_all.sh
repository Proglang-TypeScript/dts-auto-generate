#! /usr/bin/env bash

set -euo pipefail

TESTMOD="../testmodules"
RTI="/rti"

while read name; do
	#if [ "$name" == "a-big-triangle" ] || [ "$name" == "a2hs.js" ]; then
	#	continue
	#fi

	dir="$TESTMOD/$name"
	echo "$name: $dir"
	timeout -k 2 2 "$RTI/bin/runNew" "$dir" "$name" || {
		code=$?
		if [ $code -eq 124 ]; then
			echo "timeout"
		else
			break
		fi
	}
	echo
done < "../works.txt"
