import sys

class Token(object):
  def __init__(self, line_number, token_type, data = False):
    self.line_number = line_number
    self.token_type = token_type
    self.data = data
  def __repr__(self):
    if self.data:
      return "{}<{}>@{}".format(self.token_type, self.data, self.line_number)
    else:
      return "{}@{}".format(self.token_type, self.line_number)

class Scanner_error(Exception):
  def __init__(self, error):
    self.error = error
  def __str__(self):
    return 'error: ' + self.error

class Scanner(object):
  def __init__(self, filename = False):
    self.file_input = (len(filename) is 0)
    if filename:
      try:
        self.stream = open(filename, 'r')
      except IOError:
        raise Scanner_error("Could not open '{}'".format(filename))
    else:
      self.stream = sys.stdin
    self.line_number = 1
    self.eof = False
    self.reset_partial()
  def __del__(self):
    if self.file_input:
      self.stream.close()
  def reset_partial(self):
    self.integer_buffer = False
    self.identifier_buffer = False
    self.partial = ""
  def new_token(self, token_type = False, set_partial = False):
    if token_type:
      token = Token(self.line_number, token_type, self.partial)
    else:
      token = Token(self.line_number, self.partial)
    self.integer_buffer = False
    self.identifier_buffer = False
    if set_partial:
      if 'a' <= set_partial <= 'z' or 'A' <= set_partial <= 'Z':
        self.identifier_buffer = True
      elif '0' <= set_partial <= '9':
        self.integer_buffer = True
      self.partial = set_partial
    else:
      self.partial = ""
    return token
  def generate_tokens(self):
    tokens = []
    while True:
      token = self.next_token()
      if not token:
        break
      tokens.append(token)
    return tokens
  def next_token(self):
    while not self.eof:
      c = self.stream.read(1)
      if not c:
        self.eof = True
        if self.partial:
          self.line_number -= 1
          if self.integer_buffer:
            return self.new_token('integer')
          elif self.identifier_buffer:
            return self.new_token('identifier')
          elif self.partial in [';', '.', '=', ')', '+', '-', '*', '#', '[',
                                ']', ',', ':', '<', '>']:
            return self.new_token()
          else:
            raise Scanner_error("Urecognized symbol '{}' on line {}".format(
                                  self.partial, self.line_number))
        return False
      if c in [' ', '\f', '\r', '\t', '\n']:
        if c == '\n':
          self.line_number += 1
        if self.partial:
          if self.integer_buffer:
            return self.new_token('identifier')
          if self.identifier_buffer:
            return self.new_token('integer')
        continue
      if len(self.partial) >= 1:
        if self.partial in [';', '.', '=', ')', '+', '-', '*', '#', '[', ']', ',']:
          return self.new_token(set_partial = c)
        if self.partial in [':', '<', '>']:
          if c == "=":
            self.partial += c
            return self.new_token()
          return self.new_token(set_partial = c)
        if self.partial == '(':
          if c == '*':
            line_number = self.line_number
            last = False
            while True:
              c = self.stream.read(1)
              if not c:
                raise Scanner_error("The comment on line {} is not closed".format(line_number))
              elif c == '\n':
                self.line_number += 1
              elif c == '*':
                last = True
              elif last and c == ')':
                break
            self.reset_partial()
            continue
          else:
            return self.new_token(set_partial = c)
        if self.partial in ['PROGRAM', 'BEGIN', 'END', 'CONST', 'TYPE', 'VAR', 'PROCEDURE',
                            'RETURN', 'ARRAY', 'OF', 'RECORD', 'DIV', 'MOD', 'IF',
                            'THEN', 'ELSE', 'REPEAT', 'UNTIL', 'WHILE', 'DO', 'WRITE',
                            'READ']:
          return self.new_token(set_partial = c)
        if self.integer_buffer:
          if '0' <= c <= '9':
            self.partial += c
            continue
          elif 'a' <= c <= 'z' or 'A' <= c <= 'Z':
            raise Scanner_error("The identifier '{}' on line {} starts with a number".format(
                                  self.partial, self.line_number))
          return self.new_token('integer', c)
        if self.identifier_buffer:
          if 'a' <= c <= 'z' or 'A' <= c <= 'Z' or '0' <= c <= '9':
            self.partial += c
            continue
          return self.new_token('identifier', c)
        raise Scanner_error("Urecognized symbol '{}' on line {}".format(
                              self.partial, self.line_number))
      if '0' <= c <= '9':
        self.integer_buffer = True
      elif 'a' <= c <= 'z' or 'A' <= c <= 'Z':
        self.identifier_buffer = True
      self.partial += c
    return False

