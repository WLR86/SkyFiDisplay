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

# Indiserver

Todo : 
- monitor log entries ('INFO') so we can detect when a goto command is completed
- create custom LCD characters we may need eg °
- create services that takes care of launching indiserver, drivers, indi-web and ou script



apt install python3-pip swig libindi-dev python3-setuptools python3-dev
pip3 install indiweb

pip3 install pyindi-client fails (can't find lindiclient.a)

found that fucking file there : /usr/lib/arm-linux-gnueabihf
since this piece of junk looks for libs in current directory as well
I cd'ed there and retried "pip3 install pyindi-client" - and guess what ? now it want something else 

    swig -python -v -Wall -c++ -threads -I/usr/include -I/usr/include/libindi -I/usr/local/include/libindi -o indiclientpython_wrap.cpp indiclientpython.i
    indiclientpython.i:41: Error: Unable to find 'indimacros.h'
    indiclientpython.i:47: Error: Unable to find 'indiwidgettraits.h'
    indiclientpython.i:56: Error: Unable to find 'indipropertyview.h'
    indiclientpython.i:104: Error: Unable to find 'indipropertybasic.h'
    indiclientpython.i:122: Error: Unable to find 'indipropertytext.h'
    indiclientpython.i:123: Error: Unable to find 'indipropertynumber.h'
    indiclientpython.i:124: Error: Unable to find 'indipropertyswitch.h'
    indiclientpython.i:125: Error: Unable to find 'indipropertylight.h'
    indiclientpython.i:126: Error: Unable to find 'indipropertyblob.h'
    indiclientpython.i:196: Error: Unable to find 'indiproperties.h'
    Language subdirectory: python
    Search paths:
       ./
       /usr/include/
       /usr/include/libindi/
       /usr/local/include/libindi/
       ./swig_lib/python/
       /usr/share/swig3.0/python/
       ./swig_lib/
       /usr/share/swig3.0/
    Preprocessing...
    error: command 'swig' failed with exit status 1

Ok, looks like we better off code our own python client, since all this piece of shit maybe break anytime if it get to work sometime

This going nowhere, since we're running Debian 10, let's first try to upgrade to newer version and see what happens regarding indi

what's follows is just amazingly fun

Ok, let's see - Find latest bookworm debian image file - ok
Use Balena Etcher on MacOS and write this image to SDCard -> no boot
Use Balena Etcher on Windows 10 and write this image to SDCard -> no boot

Maybe this image is somehow screwed up so let's try with a older image -> same result
Maybe this image is somehow screwed up so let's try with a even older image -> same result

Ok Maybe BalenaEtcher is just a piece of shit, seems to be a pattern, everything so far was just fucked up

so back to trying latest bookworm image, using terminal tools on MacOS
sudo dd if=raspi_1_bookworm.img of=/dev/disk2 bs=1m

So far... so good - let's see if it boots

but before :
cd /Volumes/RASPIFIRM
touch ssh
vi config.txt : add last line "dtoverlay=dwc2"
vi cmdline.txt add after "rootwait" : modules_load=dwc2,g_ether

and .... still fucking boot : Led is flashing in cycle two rapid flashes and this doesn't seem be documented

I just fucking LOVE all this pile of crap

Ok, so let's try something else, I love wasting time so much
let's try Raspberry Pi Imager v1.7.5
this has some interresing features, like being able to decide the hostname, have ssh enabled, being able to add ssh keys, and even enter a SSID and a password so it can join a Wi-Fi network

Well, the system boots, which is by itself a victory, but my DHCP network haven't heard anything from the rpi
So I edited cmdline.txt and config.txt to add ether gadget feature so I can investigate, noticed there was no ssh file so I created one and restarted

... and boom this time it requested an IP address

So ... back to square one. Debian Bullseye, python3.9, Indi v1.8.8 and pyindi-client v1.9.1
and well, it still looking for those fucking .h files

pip3 install pyindi-client==0.2.8 => still doing shit
pip3 install pyindi-client==0.2.4 => totally new shit, it fails now for a whole lot of new fucking reasons, but none of the previous fucking ones
pip3 install pyindi-client==0.2.6 => takes time, but no errors so far - Oh ok it fails like shit too

sooooooo
git cloning libs from indi repo
wgetting tar.gz of release 1.9.1 of pyindi-client
modifying setup.cfg and setup.py so it gets its fucking libs
then python3 setup.py install and.... a whole pile of shit, ending nowhere because of a hundred warnings
each time a new step is achieved, a whole new world of shit appears, each one bigger and deeper than the previous one


so let's recap
Indi is coded like shit, but still seems to work
Indi-web relies on python, but still seems to work
pyindi-client may work under some specific conditions (on its dev's computer I guess)
but in my context : rapsberry pi zero W (because I don't need a fucking Cray One to get what I need to do)
Debian 10 was working fine using ser2net but is too old to run pyindi-client 1.9.1 because the way it's being built (swag) and the dependencies that can't be satisfied using apt and pip3

Debian Bullseye doesn't seem to boot
Debian Bookwork doesn't seem to boot

So what ? I have to use a fucking windows laptop ?


