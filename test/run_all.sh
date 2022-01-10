#! /usr/bin/env bash

set -euo pipefail

TESTMOD="../testmodules"
OUTPUT_DIR="../declfiles"
RTI="/rti"

trap 'exit 1' SIGINT

function process() {
	name=$1
	dir="$TESTMOD/$name"
	echo "$name: $dir"
	code=0
	DECLFILE=$(timeout -k 2 8 "$RTI/bin/runNew" "$dir" "$name") || code=$?
	case $code in
	0)
		mkdir -p "$OUTPUT_DIR/$name"
		echo "$DECLFILE" | tee "$OUTPUT_DIR/$name/index.d.ts"
		;;
	124)
		echo "timeout"
		;;
	*)
		exit 1
		;;
	esac

	echo
}

if [[ -z "${1+x}" ]]; then
	while read name; do
		[[ "$name" =~ ^#.* ]] && continue
		process "$name"
	done < "../works_filtered.txt"
else
	process "$1"
fi

