#!/usr/bin/python

# Anthony Burzillo
# aburzil1@jhu.edu
#
# sc

import sys

from src.scanner import Scanner, Scan_exception
from src.parser import Parser, Parse_exception
from src.symbol_table import Symbol_table_exception
from src.ast import AST_exception
from src.environment import Environment
from src.interpreter import Interpreter, Interpreter_exception
from src.code_generator import Code_generator
from src.improved_code_generator import Improved_code_generator

usage = "error: sc usage: ./sc [-(s | ((c | t | a) [ -g ]) | i | x)] [filename]\n"

if not len(sys.argv) <= 4: # error check the number of arguments
	sys.stderr.write(usage)
	sys.exit(1)
elif len(sys.argv) > 1 and sys.argv[1] == "-s":
	try:
		if len(sys.argv) == 2: # if no filename is given
			scanner = Scanner()
		elif sys.argv[2] == "-g":
			sys.stderr.write("error: -g cannot follow an -s\n")
			sys.exit(1)
		else: # if a filename is given
			scanner = Scanner(sys.argv[2])
		tokens = scanner.all()
		for token in tokens:
			print token
	except Scan_exception as scan_exception:
		sys.stderr.write(scan_exception.__str__() + "\n")
		sys.exit(1)
elif len(sys.argv) > 1 and sys.argv[1] == "-c":
	try:
		if len(sys.argv) == 2: # if no filename is given
			scanner = Scanner()
			tokens = scanner.all()
			parser = Parser(tokens, create_symbol_table = False, ast = False)
		elif sys.argv[2] == "-g":
			if len(sys.argv) == 3: # if no filename is given
				scanner = Scanner()
			else:
				scanner = Scanner(sys.argv[3])
			tokens = scanner.all()
			parser = Parser(tokens, True, False, False)
		else: # if a filename is given
			scanner = Scanner(sys.argv[2])
			tokens = scanner.all()
			parser = Parser(tokens)
		parser.parse()
		parser.print_tree()
	except Scan_exception as scan_exception:
		sys.stderr.write(scan_exception.__str__() + "\n")
		sys.exit(1)
	except Parse_exception as parse_exception:
		sys.stderr.write(parse_exception.__str__() + "\n")
		sys.exit(1)
	except Symbol_table_exception as symbol_table_exception:
		sys.stderr.write(symbol_table_exception.__str__() + "\n")
		sys.exit(1)
	except AST_exception as ast_exception:
		sys.stderr.write(ast_exception.__str__() + "\n")
		sys.exit(1)
elif len(sys.argv) > 1 and sys.argv[1] == "-t":
	try:
		if len(sys.argv) == 2: # if no filename is given
			scanner = Scanner()
		elif sys.argv[2] == "-g":
			if len(sys.argv) == 3: # if no filename is given
				scanner = Scanner()
			else:
				scanner = Scanner(sys.argv[3])
		else: # if a filename is given
			scanner = Scanner(sys.argv[2])
		tokens = scanner.all()
		parser = Parser(tokens, ast = False)
		symbol_table = parser.parse()
		if len(sys.argv) > 2 and sys.argv[2] == "-g":
			symbol_table.print_table(True)
		else:
			symbol_table.print_table()
	except Scan_exception as scan_exception:
		sys.stderr.write(scan_exception.__str__() + "\n")
		sys.exit(1)
	except Parse_exception as parse_exception:
		sys.stderr.write(parse_exception.__str__() + "\n")
		sys.exit(1)
	except Symbol_table_exception as symbol_table_exception:
		sys.stderr.write(symbol_table_exception.__str__() + "\n")
		sys.exit(1)
	except AST_exception as ast_exception:
		sys.stderr.write(ast_exception.__str__() + "\n")
		sys.exit(1)
elif len(sys.argv) > 1 and sys.argv[1] == "-a":
	try:
		if len(sys.argv) == 2: # if no filename is given
			scanner = Scanner()
		elif sys.argv[2] == "-g":
			if len(sys.argv) == 3: # if no filename is given
				scanner = Scanner()
			else:
				scanner = Scanner(sys.argv[3])
		else: # if a filename is given
			scanner = Scanner(sys.argv[2])
		tokens = scanner.all()
		parser = Parser(tokens)
		symbol_table, abstract_syntax_tree = parser.parse()
		if abstract_syntax_tree:
			if len(sys.argv) > 2 and sys.argv[2] == "-g":
				abstract_syntax_tree.print_tree(True)
			else:
				abstract_syntax_tree.print_tree()
	except Scan_exception as scan_exception:
		sys.stderr.write(scan_exception.__str__() + "\n")
		sys.exit(1)
	except Parse_exception as parse_exception:
		sys.stderr.write(parse_exception.__str__() + "\n")
		sys.exit(1)
	except Symbol_table_exception as symbol_table_exception:
		sys.stderr.write(symbol_table_exception.__str__() + "\n")
		sys.exit(1)
	except AST_exception as ast_exception:
		sys.stderr.write(ast_exception.__str__() + "\n")
		sys.exit(1)
elif len(sys.argv) > 1 and sys.argv[1] == "-i":
	try:
		if len(sys.argv) == 2: # if no filename is given
			scanner = Scanner()
		else: # if a filename is given
			scanner = Scanner(sys.argv[2])
		tokens = scanner.all()
		parser = Parser(tokens)
		symbol_table, abstract_syntax_tree = parser.parse()
		environment = Environment(symbol_table)
		interpreter = Interpreter(environment, abstract_syntax_tree)
		interpreter.run()
	except Scan_exception as scan_exception:
		sys.stderr.write(scan_exception.__str__() + "\n")
		sys.exit(1)
	except Parse_exception as parse_exception:
		sys.stderr.write(parse_exception.__str__() + "\n")
		sys.exit(1)
	except Symbol_table_exception as symbol_table_exception:
		sys.stderr.write(symbol_table_exception.__str__() + "\n")
		sys.exit(1)
	except AST_exception as ast_exception:
		sys.stderr.write(ast_exception.__str__() + "\n")
		sys.exit(1)
	except Interpreter_exception as interpreter_exception:
		sys.stderr.write(interpreter_exception.__str__() + "\n")
		sys.exit(1)
elif len(sys.argv) > 1 and sys.argv[1] == "-x":
	try:
		filename = False
		if len(sys.argv) == 2: # if no filename is given
			scanner = Scanner()
		else: # if a filename is given
			scanner = Scanner(sys.argv[2])
			filename = True
		tokens = scanner.all()
		parser = Parser(tokens)
		symbol_table, abstract_syntax_tree = parser.parse()
		generator = Improved_code_generator(symbol_table, abstract_syntax_tree)
		code = generator.generate()
		if filename:
			name = sys.argv[2]
			with open(name[:name.rfind(".")] + ".s", "w") as f:
				for line in code:
					f.write(line + "\n")
		else:
			for line in code:
				print line
	except Scan_exception as scan_exception:
		sys.stderr.write(scan_exception.__str__() + "\n")
		sys.exit(1)
	except Parse_exception as parse_exception:
		sys.stderr.write(parse_exception.__str__() + "\n")
		sys.exit(1)
	except Symbol_table_exception as symbol_table_exception:
		sys.stderr.write(symbol_table_exception.__str__() + "\n")
		sys.exit(1)
	except AST_exception as ast_exception:
		sys.stderr.write(ast_exception.__str__() + "\n")
		sys.exit(1)
elif len(sys.argv) > 1 and sys.argv[1] == "-g":
	sys.stderr.write("error: -g must follow -c or -t\n")
	sys.exit(1)
elif len(sys.argv) > 1 and sys.argv[1][:1] == "-":
	sys.stderr.write(usage)
	sys.exit(1)
else:
	try:
		filename = False
		if len(sys.argv) == 1: # if no filename is given
			scanner = Scanner()
		else: # if a filename is given
			scanner = Scanner(sys.argv[1])
			filename = True
		tokens = scanner.all()
		parser = Parser(tokens)
		symbol_table, abstract_syntax_tree = parser.parse()
		generator = Code_generator(symbol_table, abstract_syntax_tree)
		code = generator.generate()
		if filename:
			name = sys.argv[1]
			with open(name[:name.rfind(".")] + ".s", "w") as f:
				for line in code:
					f.write(line + "\n")
		else:
			for line in code:
				print line
	except Scan_exception as scan_exception:
		sys.stderr.write(scan_exception.__str__() + "\n")
		sys.exit(1)
	except Parse_exception as parse_exception:
		sys.stderr.write(parse_exception.__str__() + "\n")
		sys.exit(1)
	except Symbol_table_exception as symbol_table_exception:
		sys.stderr.write(symbol_table_exception.__str__() + "\n")
		sys.exit(1)
	except AST_exception as ast_exception:
		sys.stderr.write(ast_exception.__str__() + "\n")
		sys.exit(1)

