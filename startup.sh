#!/bin/bash

# Wait for networking to be ok
# doesn't work
# sleep 25

cd /home/willy

if pgrep -x "indiserver" >/dev/null
then
	echo Do nothing
else 
	indi-web &
fi

cd SkyFiDisplay
python3 queryRADECviaIndi.py
