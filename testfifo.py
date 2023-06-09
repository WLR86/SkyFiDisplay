#!/usr/bin/python3.9
import asyncio
import aiofiles
import smbus
import time
import sys
import re

LABELS_FORMAT = "other"
mode = "console"

try:
    bus = smbus.SMBus(1)
    for device in range(128):
        try:
            bus.read_byte(device)
            print(hex(device))
        except IOError.e:
            pass
except FileNotFoundError:
    pass


def hex2deg(n=""):
    value = int(int(n, 16) / 256)
    return (value / pow(2, 24)) * 360


def deg2HMS(ra="", dec="", round=True):
    RA, DEC, rs, ds = "", "", "", ""
    if dec:
        if int(dec) > 180:
            dec = dec - 360
        if str(dec)[0] == "-":
            ds, dec = "-", abs(dec)
        else:
            ds, dec = "+", abs(dec)
        deg = int(dec)
        decM = abs(int((dec - deg) * 60))
        if round:
            decS = int((abs((dec - deg) * 60) - decM) * 60)
        else:
            decS = (abs((dec - deg) * 60) - decM) * 60
        if mode == "LCD":
            DEC = "{}{:03d}ß{:02d}'{:02d}\"".format(ds, deg, decM, decS)
        else:
            DEC = "{}{:03d}°{:02d}'{:02d}\"".format(ds, deg, decM, decS)
    if ra:
        if str(ra)[0] == "-":
            rs, ra = "-", abs(ra)
        raH = int(ra / 15)
        raM = int(((ra / 15) - raH) * 60)
        if round:
            raS = int(((((ra / 15) - raH) * 60) - raM) * 60)
        else:
            raS = ((((ra / 15) - raH) * 60) - raM) * 60
        RA = "{}{:02d}h{:02d}'{:02d}\"".format(rs, raH, raM, raS)
    if ra and dec:
        return (RA, DEC)
    else:
        return RA or DEC


def decode(ra="", dec="", round=False):
    if ra and dec:
        return deg2HMS(hex2deg(ra), hex2deg(dec))
    if ra:
        return deg2HMS(ra=hex2deg(ra))
    if dec:
        return deg2HMS(dec=hex2deg(dec))


def displayConsole(ra="", dec=""):
    #  currentTime = time.strftime("%H:%M")
    #  currentDate = time.strftime("%d/%m")

    #  line1 = "  " + ra + "" + currentTime
    #  line2 = dec + "" + currentDate
    line1 = "" + ra + ""
    line2 = "" + dec + ""

    if LABELS_FORMAT == "none":
        print("\u250c" + "\u2500" * 16 + "\u2510")
        print("\u2502       " + line1 + "\u2502")
        print("\u2502     " + line2 + "\u2502")
        print("\u2514" + "\u2500" * 16 + "\u2518")
        sys.stdout.write("\u001b[4A")
        sys.stdout.write("\u001b[16D")
    elif LABELS_FORMAT == "short":
        print("  α=" + line1)
        print(" δ=" + line2)
        sys.stdout.write("\u001b[2A")
        sys.stdout.write("\u001b[16D")
    else:
        print("RA    " + line1)
        print("Dec " + line2)
        sys.stdout.write("\u001b[2A")
        sys.stdout.write("\u001b[16D")
    # time.sleep(0.025)
    sys.stdout.flush()


def display(line1, line2):
    if mode == "LCD":
        display.lcd_string(line1)
        display.lcd_string(line2)
    else:
        print(line1)
        print(line2)
        sys.stdout.write("\u001b[2A")
        sys.stdout.write("\u001b[16D")
        sys.stdout.flush()


async def read_data_stream(file):
    line_1 = ""
    line_2 = ""
    buffer = ""
    async with aiofiles.open(file, mode="r") as stream:
        while True:
            chunk = await stream.read(1)
            if not chunk:
                await asyncio.sleep(5)
                continue
            buffer += chunk
            while "#" in buffer:
                data, _, buffer = buffer.partition("#")
                getPosString = re.compile(r"e([A-F0-9\/]{8})\,([A-F,0-9]{8})")
                getPos = getPosString.match(data)
                if getPos:
                    hexRA = getPos.group(1)
                    hexDec = getPos.group(2)
                    RA = decode(ra=hexRA)
                    Dec = decode(dec=hexDec)
                    line_1 = "RA    " + RA
                    line_2 = "Dec " + Dec
                    display(line_1, line_2)


async def main():
    file = "fifo"
    display("SkyFi DSC", "(C) 2023 WLR")
    time.sleep(5)
    display("  Waiting for   ", "    Data ...    ")

    while True:
        try:
            await read_data_stream(file)
        except asyncio.CancelledError:
            print("Processus interrompu")
            break


asyncio.run(main())
