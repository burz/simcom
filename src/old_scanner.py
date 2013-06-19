import sys

class Token(object):
  def __init__(self, token_type, start_position, end_position, data):
    self.token_type = token_type
    self.start_position = start_position
    self.end_position = end_position
    self.data = data
  def __repr__(self):
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
  def __init__(self, filename = ""):
    self.file_input = not len(filename) == 0
    if self.file_input:
      try:
        self.program_file = open( filename, "r" )
      except IOError:
        raise Scan_exception("Could not open file: {}".format(filename))
    self.position = -1
    self._reset_input_string()
  def __del__(self):
    if self.file_input:
      try:
        self.program_file.close()
      except AttributeError:
        pass
  def _reset_input_string(self):
    self.digits = False
    self.symbols = False
    self.input_string = ""
  def _get_char(self):
    self.position += 1
    if self.file_input:
      return self.program_file.read(1)
    else:
      return sys.stdin.read(1)
  def _get_char_type(self, char):
    if '0' <= char <= '9':
      return "digit"
    if 'A' <= char <= 'Z' or 'a' <= char <= 'z':
      return "letter"
    else:
      return "other"
  def _get_token_type(self, string):
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
    while True:
      c = self._get_char()
      if len(c) == 0:
        return Token("eof", self.position, self.position, "")
      elif len(self.input_string) == 0:
        if c == ' ' or c == '\f' or c == '\r' or c == '\t' or c == '\n':
          continue
        c_type = self._get_char_type(c)
        if c_type == "digit":
          self.digits = True
          self.input_string = c
        elif c_type == "letter":
          self.input_string = c
        else:
          self.symbols = True
          self.input_string = c
      else:
        if c == ' ' or c == '\n' or c == '\f' or c == '\r' or c == '\t':
          start_position = self.position - len(self.input_string)
          end_position = self.position - 1
          if not self.digits:
            token_type = self._get_token_type(self.input_string)
            if self.symbols and token_type == "identifier":
              raise Scan_exception("Unknown symbol {} at ({}, {})".format(self.input_string, start_position, end_position))
            data = self.input_string
            self._reset_input_string()
          else:
            token_type = "integer"
            data = int(self.input_string)
            self._reset_input_string()
          break
        c_type = self._get_char_type(c)
        if self.digits:
          if c_type == "digit":
            self.input_string += c
          elif c_type == "letter":
            raise Scan_exception("Identifier at ({}, {})  must start with a letter; given: {}".format(self.position - len(self.input_string), self.position, self.input_string))
          else:
            token_type = "integer"
            data = int(self.input_string)
            start_position = self.position - len(self.input_string)
            end_position = self.position - 1
            self._reset_input_string()
            self.input_string = c
            self.symbols = True
            break
        elif self.symbols:
          if c_type != "other":
            token_type = self._get_token_type(self.input_string)
            if token_type == "identifier":
              raise Scan_exception("Unknown symbol {} at ({}, {})".format(self.input_string, self.position - len(self.input_string), self.position))
            start_position = self.position - len(self.input_string)
            end_position = self.position - 1
            data = self.input_string
            self._reset_input_string()
            self.input_string = c
            if c_type == "digit":
              self.digits = True
            break
          else:
            if (self.input_string == ":" or self.input_string == "<" or self.input_string == ">") and c == '=':
                self.input_string += c
                self.symbols = True
            elif self.input_string == "(" and c == "*":
              start_position = self.position - 1
              while True:
                self.input_string = c
                c = self._get_char()
                if len(c) == 0:
                  raise Scan_exception("comment at ({0}, {0}) is not closed".format(start_position))
                if self.input_string == "*" and c == ")":
                  self._reset_input_string()
                  break
            else:
              token_type = self._get_token_type(self.input_string)
              if token_type == "identifier":
                raise Scan_exception("Unknown symbol {} at ({}, {})".format(self.input_string, self.position - len(self.input_string), self.position))
              start_position = self.position - len(self.input_string)
              end_position = self.position - 1
              data = self.input_string
              self._reset_input_string()
              self.input_string = c
              self.symbols = True
              break
        else:
          if c_type != "other":
            self.input_string += c
          else:
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
    tokens = []
    while True:
      next_token = self.next()
      tokens.append(next_token)
      if next_token.token_type == "eof":
        return tokens

