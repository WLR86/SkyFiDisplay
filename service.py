#!/usr/bin/python3

import subprocess,os,time

from display import *

modeFile = '/tmp/mode'
snoopRXTXCmd = 'tailf /tmp/tb | /home/pi/SkyiDisplay/SynScanCoords.py'

def main():
    lcd_init()
    lcd_string('SkyFi+DSC Disp ', LCD_LINE_1)
    lcd_string('(C) 2018 Weetos', LCD_LINE_2)
    time.sleep(5)
    while True:
        # set an interrupt on a falling edge and wait for it to happen
        # GPIO.wait_for_edge(INT, GPIO.FALLING)

        # In the meantime, let's do it without using GPIO
        from pathlib import Path
        mode = Path(modeFile).read_text()

        if mode == 'standalone':
           # Testing
           lcd_string('Standalone mode ', LCD_LINE_1)
           lcd_string('              ON', LCD_LINE_2)
           time.sleep(4)
        else:
           lcd_string('AppDriven mode  ', LCD_LINE_1)
           lcd_string('              ON', LCD_LINE_2)
           time.sleep(2)
           exists = os.path.isfile('/tmp/tb')
           if exists:
                subprocess.call([snoopRXTXCmd], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

           else:
                time.sleep(2)
                lcd_string('Please Connect  ', LCD_LINE_1)
                lcd_string('Client App      ', LCD_LINE_2)
                time.sleep(4)
                lcd_string('Waiting         ', LCD_LINE_1)
                lcd_string('for data ...    ', LCD_LINE_2)
                time.sleep(2)
if __name__ == '__main__':
    main()
