#!/usr/bin/python

import sys

from src.scanner import Scanner, Scanner_error

usage = "error: sc usage: ./sc [-(s | ((c | t | a) [ -g ]) | i | x)] [filename]\n"

if not len(sys.argv) <= 4: # error check the number of arguments
  sys.stderr.write(usage)
  sys.exit(1)
else:
  try:
    if len(sys.argv) > 1:
      scanner = Scanner(sys.argv[1])
    else:
      scanner = Scanner()
    tokens = scanner.generate_tokens()
    for token in tokens:
      print token
  except Scanner_error as error:
    sys.stderr.write(error.__str__() + "\n")
    sys.exit(1)

