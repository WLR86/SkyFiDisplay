# SkyFi-like adapter prototype

This is a proof of concept of a device that allows controlling a Sky-Watcher
SynScan equatorial mount from SkySafari running on a smartphone.

As a bonus, this device would display current coordinates on a 16x2 LCD dot
matrix display.

This project is an attempt to snoop into serial dialog, detect getPreciseRaDec
commands and convert then display RA and Dec on a LCD Display.

getDateTime :

```
00006430: 3345 3038 4535 3030 2356 2330 3432 3730  3E08E500#V#04270
00006440: 3523 7400 2348 1025 2a0c 0212 0100 2357  5#t.#H.%*.....#W Q=10 R=25 S=2a T=0c U=02 V=12 W=01 X=00
00006450: 2e23 1000 0017 0300 2365 4135 3330 4446  .#......#eA530DF
```
Q=10 R=25 S=2a : 0x10 0x25 0x2a > 16:37:42
T=0c (12) U=02 (02) V=12 (18) > 02/12/18
W=01 (01) > GMT+1
X=00 (00) > Standard Time (No Daylight Savings)

T is the month.
U is the day.
V is the year (century assumed as 20).
W is the offset from GMT for the time zone. Note: if zone is negative, use 256-zone.
X is 1 to enable Daylight Savings and 0 for Standard Time.

# Ideas and links

## Sky-Watcher SynScan protocol
https://inter-static.skywatcher.com/downloads/synscanserialcommunicationprotocol_version33.pdf

## Plate solving
https://www.qhyccd.com/bbs/index.php?topic=4209.0

## Similar project
https://github.com/iscrow/Astra

# Multiple network context : if none of known SSID is there, then create an AccessPoint with a DHCP server
https://raspberrypi.stackexchange.com/questions/100195/automatically-create-hotspot-if-no-network-is-available
https://www.raspberryconnect.com/projects/65-raspberrypi-hotspot-accesspoints/157-raspberry-pi-auto-wifi-hotspot-switch-internet

# New LCD lib
https://circuitdigest.com/microcontroller-projects/interfacing-lcd-with-raspberry-pi-4-to-create-custom-character-and-scrolling-text

# Indiserver

Todo : 
- monitor log entries ('INFO') so we can detect when a goto command is completed
- create custom LCD characters we may need eg °
- create services that takes care of launching indiserver, drivers, indi-web and ou script
- Improve mDNS behavior : most of the time name resolving fails, which was not the cas before
- verify time and location are being sent and taken into account when skysafari establishes its connection

Install INDI from sources instead of deb package (too old)
Otherwise PyIndi-Client won't compile

# INDIServer (extract from [https://docs.indilib.org/drivers/properties.html])
All communication in INDI is done by updating properties, so this is a really important part of the tutorial. If you want your driver to do anything at all, you'll need to understand this concept. This is also the longest part of the tutorial, but stick with it, or you're gonna have a bad time.

All properties have a name and a label, as well as a group and state.

- *name* is the code friendly name of the property.

- *label* is the human friendly name of the property.

- *group* is the human friendly name of the tab the property is on. The DefaultDevice class has some nice helpers for commonly used tabs, but feel free to add your own custom tab.

Vectors

All properties are vectors (array like object). I'll say that again: ALL PROPERTIES ARE VECTORS. A property vector can have one or more values. All values have a name and a label as well. There are Number, Text, Switch, Light, and BLOB properties.
