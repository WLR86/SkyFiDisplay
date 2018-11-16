#! /usr/local/bin/python3
# vim: set fileencoding=utf-8 autoindent expandtab tabstop=2 shiftwidth=2 softtabstop=2 :

import string, time, sys, re

CHUNK_SIZE = 20

def hex2deg(n=''):
  value = int(int(n,16)/256)
  return (value/pow(2,24))*360

def deg2HMS(ra='', dec='', round=True):
  RA, DEC, rs, ds = '', '', '', ''
  if dec:
    if str(dec)[0] == '-':
      ds, dec = '-', abs(dec)
    deg = int(dec)
    decM = abs(int((dec-deg)*60))
    if round:
      decS = int((abs((dec-deg)*60)-decM)*60)
    else:
      decS = (abs((dec-deg)*60)-decM)*60
    DEC = '{}{:02d}°{:02d}:{:02d}'.format(ds, deg, decM, decS)
  if ra:
    if str(ra)[0] == '-':
      rs, ra = '-', abs(ra)
    raH = int(ra/15)
    raM = int(((ra/15)-raH)*60)
    if round:
      raS = int(((((ra/15)-raH)*60)-raM)*60)
    else:
      raS = ((((ra/15)-raH)*60)-raM)*60
    RA = '{}{:02d}h{:02d}m{:02d}s'.format(rs, raH, raM, raS)
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

def loopDecode():
  for spot in spots:
    trimmedInput = spot[1:-1]
    coord = trimmedInput.split(',')
    hexRA  = coord[0]
    hexDec = coord[1]
    print(" RA:",decode(ra=hexRA))
    print("Dec:",decode(dec=hexDec))

if __name__ == '__main__':
  myFile = sys.stdin
  for chunk in each_chunk(myFile, separator='#'):
    string = re.compile(r"e([A-F0-9\/]{8})\,([A-F,0-9]{8})")
    s = string.match(chunk)
    if s:
      hexRA  = s.group(1)
      hexDec = s.group(2)
      RA     = decode(ra=hexRA)
      Dec    = decode(dec=hexDec)
      #  hexRA = "FA263700"
      #  hexDec = "3E15D100"
      #  RA =  (int(int(hexRA ,16)/256)/16777216)*360
      #  Dec = (int(int(hexDec,16)/256)/16777216)*360
      print( ' RA:' + str(RA)  )
      print( 'Dec:' + str(Dec) )


