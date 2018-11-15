#!/usr/bin/python
import re, sys

#  testing = re.compile(r"e([A-F0-9\/]{8})\,([A-F,0-9]{8})#")
print(re.search(r"e([A-F0-9\/]{8})\,([A-F,0-9]{8})#",sys.stdin.readline()))

if testing:
  RA = testing.group(1)
  Dec = testing.group(2)
  print("RA ",RA)
  print("Dec",Dec)

