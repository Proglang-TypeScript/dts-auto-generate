#! /usr/bin/env bash

set -euo pipefail

TESTMOD="testmodules"

for dir in $TESTMOD/*; do
	name=${dir#"$TESTMOD/"}
	echo "$name:"
	timeout -k 2 2 node main.js "$dir" "$name" > /dev/null 2>&1 || true
	cat out.txt
	echo
done
