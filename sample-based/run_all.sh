#! /usr/bin/env bash

set -euo pipefail

TESTMOD="testmodules"

for dir in $TESTMOD/*; do
	name=${dir#"$TESTMOD/"}
	echo "$name:"
	node main.js "$dir" "$name" || true
	echo
done
