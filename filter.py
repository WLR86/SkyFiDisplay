#!/usr/local/bin/python3
# vim: set fileencoding=utf-8 autoindent expandtab tabstop=2 shiftwidth=2 softtabstop=2 :

import re, sys

CHUNK_SIZE = 20

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

myFile = sys.stdin
for chunk in each_chunk(myFile, separator='#'):
  string = re.compile(r"e([A-F0-9\/]{8})\,([A-F,0-9]{8})")
  s = string.match(chunk)
  if s:
    RA = s.group(1)
    Dec = s.group(2)
    print("RA ",RA)
    print("Dec",Dec)

