# SkyFi-like adaptor prototype

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
