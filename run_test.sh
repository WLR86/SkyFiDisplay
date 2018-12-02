#!/bin/bash
file=dump2.data

# Use actual captured data
if [ "$1" == "file" ] && [ -f $file ]; then
	clear; echo; echo; cat $file | ./SynScanCoords.py
else

	# Use a loop of fake data
	clear; echo; echo; ./emulate_stream.py | ./SynScanCoords.py
fi
