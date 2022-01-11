#! /usr/local/bin/python3
# vim: set fileencoding=utf-8 autoindent expandtab tabstop=2 shiftwidth=2 softtabstop=2 filetype=python :

import string, time, sys, re, smbus, subprocess, datetime

from disp_config import *

mode = sys.argv[1] # Could be console or LCD
if mode == 'LCD':
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
    if mode == 'LCD':
      DEC = "{}{:03d}ß{:02d}'{:02d}\"".format(ds, deg, decM, decS)
    else:
      DEC = "{}{:03d}°{:02d}'{:02d}\"".format(ds, deg, decM, decS)
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

def displayConsole(ra='',dec=''):
  currentTime = time.strftime('%H:%M')
  currentDate = time.strftime('%d/%m')

  line1 = '  ' + ra + '' + currentTime
  line2 = dec + '' + currentDate

  if LABELS_FORMAT == 'none':
    print( u'\u250c' + u'\u2500'*16 + u'\u2510' )
    print( u'\u2502' + line1 + u'\u2502' )
    print( u'\u2502' + line2 + u'\u2502' )
    print( u'\u2514' + u'\u2500'*16 + u'\u2518' )
  elif LABELS_FORMAT == 'short':
    print( u' α=' + line1 )
    print( u' δ=' + line2 )
  else:
    print( u' RA=' + line1 )
    print( u'Dec=' + line2 )
  sys.stdout.write( u"\u001b[4A" )
  sys.stdout.write( u"\u001b[16D" )
  # This timer is aimed at slowing down the output when simulating data from a
  # dump file - Not needed when outputing to LCD
  time.sleep(0.025)
  sys.stdout.flush()

def displayLCD(ra='',dec=''):
    currentTime = time.strftime('%H:%M')
    currentDate = time.strftime('%d/%m')
    lcd_string(' ' + ra + ' ' + currentTime,LCD_LINE_1)
    lcd_string(dec + ' ' + currentDate,LCD_LINE_2)

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

def setDateTime(dateTime):
  subprocess.call(['date +"%Y-%m-%d %H:%m:%S" -s "' + dateTime +'"'],shell=True, \
       stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def setDateTimeFromCode(getDateTime):
  t = [0,0,0,0,0,0]
  for x in range(1,7):
    t.append(int.from_bytes(getDateTime.group(x),byteorder='little'))
  currentDateTime = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(t[6], t[5], t[4], t[1], t[2], t[3])
  setDateTime(dateTime=currentDateTime)

def loopDecode():
  for spot in spots:
    trimmedInput = spot[1:-1]
    coord = trimmedInput.split(',')
    hexRA  = coord[0]
    hexDec = coord[1]
    print(" RA:",decode(ra=hexRA))
    print("Dec:",decode(dec=hexDec))

if __name__ == '__main__':
  if mode == 'LCD':
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
      if mode == 'LCD':
        displayLCD(ra=RA,dec=Dec)
      else:
        displayConsole(ra=RA,dec=Dec)
    getDateTime = re.match(b'^\x48([\0-\xFF])([\0-\xFF])([\0-\xFF])([\0-\xFF])([\0-\xFF])([\0-\xFF])([\0-\xFF])([\0-\xFF])',chunk.encode())
    if getDateTime:
      setDateTimeFromCode(getDateTime)

