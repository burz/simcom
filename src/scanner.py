# Anthony Burzillo
# aburzil1@jhu.edu
#
# scanner.py

import sys

class Token(object):
  """Holds a token produced by the scanner"""
  def __init__(self, token_type, start_position, end_position, data):
    """Creates a token.

    token_type := the name of the type of token
    start_position := the starting position of the token in the program
    end_position := the ending position of the token in the program
    data := the data held by the token (i.e. 6778 or "x")

    """
    self.token_type = token_type
    self.start_position = start_position
    self.end_position = end_position
    self.data = data
  def __repr__(self):
    """Return a string describing the token"""
    if self.token_type == "integer" or self.token_type == "identifier":
      return "{}<{}>@({}, {})".format(self.token_type, self.data, self.start_position, self.end_position)
    else:
      return "{}@({}, {})".format(self.token_type, self.start_position, self.end_position)

class Scan_exception(Exception):
  def __init__(self, error):
    self.error = error
  def __str__(self):
    return "error: " + self.error

class Scanner(object):
  """Reads from some input and produces tokens"""
  def __init__(self, filename = ""):
    """Creates a scanner

    filename := the filename to read from

    Raises a Scan_exception if an error occurs

    """
    self.file_input = not len(filename) == 0
    if self.file_input: # read from a file
      try:
        self.program_file = open( filename, "r" )
      except IOError:
        raise Scan_exception("Could not open file: {}".format(filename))
    self.position = -1
    self._reset_input_string()
  def __del__(self):
    if self.file_input: # if we have a file open
      try:
        self.program_file.close()
      except AttributeError:
        pass
  def _reset_input_string(self):
    self.digits = False # the last input was not digits
    self.symbols = False # the last inupt was not symbols
    self.input_string = "" # next input
  def _get_char(self): # get the next character from the input
    self.position += 1
    if self.file_input:
      return self.program_file.read(1)
    else:
      return sys.stdin.read(1)
  def _get_char_type(self, char): # find out the type of character
    if '0' <= char <= '9':
      return "digit"
    if 'A' <= char <= 'Z' or 'a' <= char <= 'z':
      return "letter"
    else:
      return "other"
  def _get_token_type(self, string): # check if a string is recognized
    if string == "PROGRAM" or string == ";" or string == "BEGIN" or string == "END" or string == ".":
      return string
    elif string == "CONST" or string == "=" or string == "TYPE" or string == "VAR" or string == ":":
      return string
    elif string == "ARRAY" or string == "OF" or string == "RECORD":
      return string
    elif string == "+" or string == "-" or string == "*" or string == "DIV" or string == "MOD" or string == "(" or string == ")":
      return string
    elif string == ":=" or string == "IF" or string == "THEN" or string == "ELSE" or string == "REPEAT" or string == "UNTIL":
      return string
    elif string == "WHILE" or string == "DO" or string == "=" or string == "#" or string == "<" or string == ">":
      return string
    elif string == "<=" or string == ">=" or string == "WRITE" or string == "WRITE" or string == "READ":
      return string
    elif string == "[" or string == "]" or string == "," or string == "PROCEDURE" or string == "RETURN":
      return string
    else:
      return "identifier"
  def next(self):
    """Return the next token in the program

    Raises a Scan_exception if an error occurs

    """
    while True:
      c = self._get_char() # get the next character
      if len(c) == 0: # if we have reached the end of the file
        return Token("eof", self.position, self.position, "")
      elif len(self.input_string) == 0: # there is no input left in the string
        if c == ' ' or c == '\f' or c == '\r' or c == '\t' or c == '\n':
          continue
        c_type = self._get_char_type(c) # find out what type the character is
        if c_type == "digit":
          self.digits = True
          self.input_string = c
        elif c_type == "letter":
          self.input_string = c
        else: # the character is a symbol
          self.symbols = True
          self.input_string = c
      else: # if there is input left in the string
        if c == ' ' or c == '\n' or c == '\f' or c == '\r' or c == '\t':
          start_position = self.position - len(self.input_string)
          end_position = self.position - 1
          if not self.digits: # if the last input was not digits
            token_type = self._get_token_type(self.input_string)
            if self.symbols and token_type == "identifier": # if the symbol is not recognized
              raise Scan_exception("Unknown symbol {} at ({}, {})".format(self.input_string, start_position, end_position))
            data = self.input_string
            self._reset_input_string()
          else: # the last input was digits
            token_type = "integer"
            data = int(self.input_string)
            self._reset_input_string()
          break
        c_type = self._get_char_type(c) # the type of the character
        if self.digits: # if the last input was digits
          if c_type == "digit": # if the character is a digit
            self.input_string += c
          elif c_type == "letter":  # if the character is a letter
            raise Scan_exception("Identifier at ({}, {})  must start with a letter; given: {}".format(self.position - len(self.input_string), self.position, self.input_string))
          else: # if the character is a symbol
            token_type = "integer"
            data = int(self.input_string)
            start_position = self.position - len(self.input_string)
            end_position = self.position - 1
            self._reset_input_string()
            self.input_string = c
            self.symbols = True
            break
        elif self.symbols: # if the last input was symbols
          if c_type != "other": # if the input was not a symbol
            token_type = self._get_token_type(self.input_string)
            if token_type == "identifier": # the last input is not a recognized symbol
              raise Scan_exception("Unknown symbol {} at ({}, {})".format(self.input_string, self.position - len(self.input_string), self.position))
            start_position = self.position - len(self.input_string)
            end_position = self.position - 1
            data = self.input_string
            self._reset_input_string()
            self.input_string = c
            if c_type == "digit": # if the character is a digit
              self.digits = True
            break
          else: # if the character is a symbol
            if (self.input_string == ":" or self.input_string == "<" or self.input_string == ">") and c == '=': # if the last input is part of a double symbol
                self.input_string += c
                self.symbols = True
            elif self.input_string == "(" and c == "*": # if we have encountered a comment
              start_position = self.position - 1
              while True: # skip the comment
                self.input_string = c
                c = self._get_char()
                if len(c) == 0: # if we have reached the end of the file
                  raise Scan_exception("comment at ({0}, {0}) is not closed".format(start_position))
                if self.input_string == "*" and c == ")": # if we have reached the end of a comment
                  self._reset_input_string()
                  break
            else: # we have a new symbol
              token_type = self._get_token_type(self.input_string)
              if token_type == "identifier": # the last input is an unrecognized symbol
                raise Scan_exception("Unknown symbol {} at ({}, {})".format(self.input_string, self.position - len(self.input_string), self.position))
              start_position = self.position - len(self.input_string)
              end_position = self.position - 1
              data = self.input_string
              self._reset_input_string()
              self.input_string = c
              self.symbols = True
              break
        else: # if the last input was an identifier
          if c_type != "other": # if the character is a letter or a digit
            self.input_string += c
          else: # if the character is a symbol
            token_type = self._get_token_type(self.input_string)
            data = self.input_string
            start_position = self.position - len(self.input_string)
            end_position = self.position - 1
            self._reset_input_string()
            self.input_string = c
            self.symbols = True
            break
    return Token(token_type, start_position, end_position, data)
  def all(self):
    """Return all of the tokens in the program

    Returns a list of tokens

    Raises a Scan_exception if an error occurs

    """
    tokens = []
    while True:
      next_token = self.next()
      tokens.append(next_token)
      if next_token.token_type == "eof":
        return tokens

