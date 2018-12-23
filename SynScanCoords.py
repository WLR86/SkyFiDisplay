#! /usr/local/bin/python3
# vim: set fileencoding=utf-8 autoindent expandtab tabstop=2 shiftwidth=2 softtabstop=2 :

import string, time, sys, re, smbus, subprocess

from display import *

def hex2deg(n=''):
  value = int(int(n,16)/256)
  return (value/pow(2,24))*360

def deg2HMS(ra='', dec='', round=True):
  RA, DEC, rs, ds = '', '', '', ''
  if dec:
    if int(dec) > 180:
      dec = dec - 360
    if str(dec)[0] == '-':
      ds, dec = '-', abs(dec)
    else:
      ds, dec = '+', abs(dec)
    deg = int(dec)
    decM = abs(int((dec-deg)*60))
    if round:
      decS = int((abs((dec-deg)*60)-decM)*60)
    else:
      decS = (abs((dec-deg)*60)-decM)*60
    DEC = "{}{:02d}ß{:02d}'{:02d}\"".format(ds, deg, decM, decS)
  if ra:
    if str(ra)[0] == '-':
      rs, ra = '-', abs(ra)
    raH = int(ra/15)
    raM = int(((ra/15)-raH)*60)
    if round:
      raS = int(((((ra/15)-raH)*60)-raM)*60)
    else:
      raS = ((((ra/15)-raH)*60)-raM)*60
    RA = "{}{:02d}h{:02d}'{:02d}\"".format(rs, raH, raM, raS)
  if ra and dec:
    return (RA, DEC)
  else:
    return RA or DEC

def decode(ra='',dec='',round=False):
  if ra and dec:
    return deg2HMS(hex2deg(ra),hex2Angle(dec))
  if ra:
    return deg2HMS(ra=hex2deg(ra))
  if dec:
    return deg2HMS(dec=hex2deg(dec))

def displayConsole(ra='',dec='',labels='short'):
  if labels == 'short':
    print( u' α=  ' + ra + '     ' )
    print( u' δ= ' + dec + '     ' )
  else:
    print( u' RA=  ' + ra + '     ' )
    print( u'Dec= ' + dec + '     ' )
  sys.stdout.write( u"\u001b[2A" )
  sys.stdout.write( u"\u001b[30D" )
  # This timer is aimed at slowing down the output when simulating data from a
  # dump file - Remove this on production
  time.sleep(0.05)
  sys.stdout.flush()

def displayLCD(ra='',dec='',mode='app'):
  if mode == 'auto':
    currentTime = time.strftime('%H:%M')
    lcd_string(' ' + ra + '  AUTO', LCD_LINE_1)
    lcd_string(dec + ' J2000' , LCD_LINE_2)
  else:
    currentTime = time.strftime('%H:%M')
    lcd_string(' ' + ra + ' ' + currentTime,LCD_LINE_1)
    lcd_string(dec + ' J2000' ,LCD_LINE_2)


def each_chunk(stream, separator):
  buffer = ''
  while True:  # until EOF
    chunk = stream.read(CHUNK_SIZE)  # I propose 4096 or so
    if not chunk:  # EOF?
      yield buffer
      break
    buffer += chunk
    while True:  # until no separator is found
      try:
        part, buffer = buffer.split(separator, 1)
      except ValueError:
        break
      else:
        yield part

#  def main():
    #  ser = serial.Serial(SERIAL_PORT, SERIAL_RATE)
    #  while True:
        #  # using ser.readline() assumes each line contains a single reading
        #  # sent using Serial.println() on the Arduino
        #  reading = ser.readline().decode('utf-8')
        #  # reading is a string...do whatever you want from here
        #  print(reading)
def setDateTime(dateTime):
  subprocess.call(['date +"%Y-%m-%d %H:%m:%S" -s "' + dateTime +'"'],shell=True, \
       stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def loopDecode():
  for spot in spots:
    trimmedInput = spot[1:-1]
    coord = trimmedInput.split(',')
    hexRA  = coord[0]
    hexDec = coord[1]
    print(" RA:",decode(ra=hexRA))
    print("Dec:",decode(dec=hexDec))

if __name__ == '__main__':
  lcd_init()
  myFile = sys.stdin
  for chunk in each_chunk(myFile, separator='#'):
    getPosString = re.compile(r"e([A-F0-9\/]{8})\,([A-F,0-9]{8})")
    getPos = getPosString.match(chunk)
    if getPos:
      hexRA  = getPos.group(1)
      hexDec = getPos.group(2)
      RA     = decode(ra=hexRA)
      Dec    = decode(dec=hexDec)
      #  print( ' RA:' + str(RA)  )
      #  print( 'Dec:' + str(Dec) )
      displayLCD(ra=RA,dec=Dec)
    getDateTime = re.match(b'^\x48([\0-\xFF])([\0-\xFF])([\0-\xFF])([\0-\xFF])([\0-\xFF])([\0-\xFF])([\0-\xFF])([\0-\xFF])',chunk.encode())
    if getDateTime:
      Hours =   int.from_bytes(getDateTime.group(1),byteorder='little')
      Minutes = int.from_bytes(getDateTime.group(2),byteorder='little')
      Seconds = int.from_bytes(getDateTime.group(3),byteorder='little')
      Month =   int.from_bytes(getDateTime.group(4),byteorder='little')
      Day =     int.from_bytes(getDateTime.group(5),byteorder='little')
      Year =    int.from_bytes(getDateTime.group(6),byteorder='little') + 2000
      currentDateTime = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(Year, Month, Day, Hours, Minutes, Seconds)
      setDateTime(dateTime=currentDateTime)

