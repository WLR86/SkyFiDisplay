#!/bin/bash

service LCD stop
service ser2net stop
rm /tmp/tb
service ser2net start
service LCD start
