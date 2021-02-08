#!/bin/bash
file=$1
out=$2

if [ "$2" == "LCD" ]; then
	out="LCD"
else
	out="Console"
fi

# Use actual captured data
if [ -f $file ]; then
	clear; echo; echo; cat $file | ./SynScanCoords.py $out
else

	# Use a loop of fake data
	clear; echo; echo; ./emulate_stream.py | python3 ./SynScanCoords.py $out
fi
