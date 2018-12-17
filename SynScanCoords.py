#! /usr/local/bin/python3
# vim: set fileencoding=utf-8 autoindent expandtab tabstop=2 shiftwidth=2 softtabstop=2 :

import string, time, sys, re, smbus

from display import *

#  CHUNK_SIZE = 20

#  # Define some device parameters
#  I2C_ADDR  = 0x27 # I2C device address, if any error, change this address to 0x3f
#  LCD_WIDTH = 16   # Maximum characters per line

#  # Define some device constants
#  LCD_CHR = 1 # Mode - Sending data
#  LCD_CMD = 0 # Mode - Sending command

#  LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
#  LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line
#  LCD_LINE_3 = 0x94 # LCD RAM address for the 3rd line
#  LCD_LINE_4 = 0xD4 # LCD RAM address for the 4th line

#  LCD_BACKLIGHT  = 0x08  # On
#  #  LCD_BACKLIGHT = 0x00  # Off

#  ENABLE = 0b00000100 # Enable bit

#  # Timing constants
#  E_PULSE = 0.0005
#  E_DELAY = 0.0005

#  #Open I2C interface
#  #bus = smbus.SMBus(0)  # Rev 1 Pi uses 0
#  bus = smbus.SMBus(1) # Rev 2 Pi uses 1

#  def lcd_init():
  #  # Initialise display
  #  lcd_byte(0x33,LCD_CMD) # 110011 Initialise
  #  lcd_byte(0x32,LCD_CMD) # 110010 Initialise
  #  lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
  #  lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off 
  #  lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
  #  lcd_byte(0x01,LCD_CMD) # 000001 Clear display
  #  time.sleep(E_DELAY)

#  def lcd_byte(bits, mode):
  #  # Send byte to data pins
  #  # bits = the data
  #  # mode = 1 for data
  #  #        0 for command

  #  bits_high = mode | (bits & 0xF0) | LCD_BACKLIGHT
  #  bits_low = mode | ((bits<<4) & 0xF0) | LCD_BACKLIGHT

  #  # High bits
  #  bus.write_byte(I2C_ADDR, bits_high)
  #  lcd_toggle_enable(bits_high)

  #  # Low bits
  #  bus.write_byte(I2C_ADDR, bits_low)
  #  lcd_toggle_enable(bits_low)

#  def lcd_toggle_enable(bits):
  #  # Toggle enable
  #  time.sleep(E_DELAY)
  #  bus.write_byte(I2C_ADDR, (bits | ENABLE))
  #  time.sleep(E_PULSE)
  #  bus.write_byte(I2C_ADDR,(bits & ~ENABLE))
  #  time.sleep(E_DELAY)

#  def lcd_string(message,line):
  #  # Send string to display

  #  message = message.ljust(LCD_WIDTH," ")

  #  lcd_byte(line, LCD_CMD)

  #  for i in range(LCD_WIDTH):
    #  lcd_byte(ord(message[i]),LCD_CHR)

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

def displayLCD(ra='',dec='',labels='short'):

    lcd_string(' ' + ra,LCD_LINE_1)
    lcd_string(dec,LCD_LINE_2)

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
  lcd_init()
  myFile = sys.stdin
  for chunk in each_chunk(myFile, separator='#'):
    string = re.compile(r"e([A-F0-9\/]{8})\,([A-F,0-9]{8})")
    s = string.match(chunk)
    if s:
      hexRA  = s.group(1)
      hexDec = s.group(2)
      RA     = decode(ra=hexRA)
      Dec    = decode(dec=hexDec)
      #  print( ' RA:' + str(RA)  )
      #  print( 'Dec:' + str(Dec) )
      #  displayConsole(ra=RA,dec=Dec,labels='long')
      displayLCD(ra=RA,dec=Dec,labels='long')


