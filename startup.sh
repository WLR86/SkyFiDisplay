#!/bin/bash

# Wait for networking to be ok
sleep 20

cd /home/willy

if pgrep -x "indiserver" >/dev/null
then
	echo Do nothing
else 
	indi-web &
fi

cd SkyFiDisplay
python3 queryRADECviaIndi.py
