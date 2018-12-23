#!/usr/bin/python3
# vim: set fileencoding=utf-8 autoindent expandtab tabstop=2 shiftwidth=2 softtabstop=2 :

import subprocess,os,time,pexpect,logging,re

from display import *
from SynScanCoords import *

modeFile = '/tmp/mode'
mode='standalone'
host = 'localhost'
port = '11880'
snoopRXTXCmd = '/bin/tailf /tmp/tb | /home/pi/SkyFiDisplay/SynScanCoords.py'
# logging
LOG = "/tmp/lcd.log"
logging.basicConfig(filename=LOG, filemode="w", level=logging.DEBUG)

def main():
  lcd_init()
  lcd_string('SkyFi+DSC Disp ', LCD_LINE_1)
  lcd_string('(C) 2018 Weetos', LCD_LINE_2)
  time.sleep(5)
  while True:
    # set an interrupt on a falling edge and wait for it to happen
    # GPIO.wait_for_edge(INT, GPIO.FALLING)
    # In the meantime, let's do it without using GPIO
    #  from pathlib import Path
    #  mode = Path(modeFile).read_text()

    if mode == 'standalone':
      lcd_string('Standalone mode ', LCD_LINE_1)
      lcd_string('              ON', LCD_LINE_2)
      time.sleep(4)
      child = pexpect.spawn('nc %s %s'%(host, port))
      # It's now ok to get date and time from the SynScan ('h' query)
      child.sendline('h\x04')
      child.expect('#')
      chunk = child.before.decode('utf-8').replace('\r\n','')
      getDateTime = re.match(b'^\x68([\0-\xFF])([\0-\xFF])([\0-\xFF])([\0-\xFF])([\0-\xFF])([\0-\xFF])([\0-\xFF])([\0-\xFF])',chunk.encode())

      if getDateTime:
        setDateTimeFromCode(getDateTime)

      while True:
        child.sendline ('e\x04')
        child.expect ('#')
        child.sendline ('e\x04')
        getPosString = re.compile(r"e([A-F0-9\/]{8})\,([A-F,0-9]{8})#")
        getPos = getPosString.match(chunk)
        if getPos:
          hexRA  = getPos.group(1)
          hexDec = getPos.group(2)
          RA     = decode(ra=hexRA)
          Dec    = decode(dec=hexDec)
          displayLCD(ra=RA,dec=Dec,mode='auto_disabled')
          #  logging.debug(chunk)
          time.sleep(2)

    else:
      lcd_string('AppDriven mode  ', LCD_LINE_1)
      lcd_string('              ON', LCD_LINE_2)
      time.sleep(2)
      exists = os.path.isfile('/tmp/tb')
      if exists:
        subprocess.call([snoopRXTXCmd], shell=True)

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
