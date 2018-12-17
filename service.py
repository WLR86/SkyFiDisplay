#!/usr/bin/python3

import subprocess,os,time

from display import *

def main():
    lcd_init()
    lcd_string("SkyFi Weetos",LCD_LINE_1)
    lcd_string("(C) 2018",LCD_LINE_2)
    time.sleep(5)
    while True:
        # set an interrupt on a falling edge and wait for it to happen
        # GPIO.wait_for_edge(INT, GPIO.FALLING)

        exists = os.path.isfile('/tmp/tb')
        if exists:
            # Store configuration file values
            subprocess.call(['tailf /tmp/tb | /home/pi/SkyFiDisplay/SynScanCoords.py'], shell=True, \
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        else:
            time.sleep(2)
            #  print('waiting...')
            lcd_string("Waiting",LCD_LINE_1)
            lcd_string("for data...",LCD_LINE_2)


if __name__ == '__main__':
    main()
