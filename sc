#!/usr/bin/python

import sys

from src.scanner import Scanner, Scanner_error
from src.parser import Parser, Parser_error
from src.interpreter import Interpreter, Interpreter_error
from src.lazy_generator import Lazy_generator

usage = "error: sc usage: ./sc [-(s: | t | a | i | l)] [filename]\n"

filename = False
table = False
tree = False
interpret = False
lazy_compile = False
compile = False

if not len(sys.argv) <= 3: # error check the number of arguments
  sys.stderr.write(usage)
  sys.exit(1)
elif len(sys.argv) is 1:
  table = tree = compile = True
elif len(sys.argv) is 2 and not sys.argv[1] in ['-s', '-t', '-a', '-i', '-l']:
  filename = sys.argv[1]
  table = tree = compile = True
else:
  if sys.argv[1] == '-s':
    pass
  elif sys.argv[1] == '-t':
    table = True
  elif sys.argv[1] == '-a':
    table = tree = True
  elif sys.argv[1] == '-i':
    table = tree = interpret = True
  elif sys.argv[1] == '-l':
    table = tree = lazy_compile = True
  elif sys.argv[1][0] == '-':
    sys.stderr.write(usage)
    sys.exit(1)
  else:
    table = tree = compile = True
  if len(sys.argv) is 3:
    filename = sys.argv[2]
  elif len(sys.argv) is 2 and compile:
    filename = sys.argv[1]

try:
  scanner = Scanner(filename)
  tokens = scanner.generate_tokens()
  if not table:
    for token in tokens:
      print token
  else:
    parser = Parser()
    syntax_tree, symbol_table = parser.parse_tokens(tokens)
    if not tree:
      symbol_table.graphical()
      pass
    elif tree and not interpret and not lazy_compile and not compile:
      syntax_tree.graphical()
    elif interpret:
      interpreter = Interpreter()
      interpreter.run(syntax_tree, symbol_table)
    elif lazy_compile:
      compiler = Lazy_generator()
      code = compiler.generate(syntax_tree, symbol_table)
      for line in code:
        print line
      print
    else:
      pass
except Scanner_error as error:
  sys.stderr.write(error.__str__() + "\n")
  sys.exit(1)
except Parser_error as error:
  sys.stderr.write(error.__str__() + "\n")
  sys.exit(1)
except Interpreter_error as error:
  sys.stderr.write(error.__str__() + "\n")
  sys.exit(1)

