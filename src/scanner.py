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
    return "error: {}".format(self.error)

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
    self.integer_partial = False
    self.identifier_partial = False
    self.partial = ""
  def create_token(self, token_type = False, set_partial = False):
    if token_type:
      token = Token(self.line_number, token_type, self.partial)
    else:
      token = Token(self.line_number, self.partial)
    self.integer_partial = False
    self.identifier_partial = False
    if set_partial:
      if 'a' <= set_partial <= 'z' or 'A' <= set_partial <= 'Z':
        self.identifier_partial = True
      elif '0' <= set_partial <= '9':
        self.integer_partial = True
      self.partial = set_partial
    else:
      self.partial = ""
    return token
  def partial_to_token(self, c = False):
    if self.partial in [';', '.', '=', ')', '+', '-', '*', '#', '[', ']', ',']:
      return self.create_token(set_partial = c)
    elif self.partial in [':', '<', '>']:
      if c == "=":
        self.partial += c
        return self.create_token()
      return self.create_token(set_partial = c)
    elif self.partial == '(':
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
      else:
        return self.create_token(set_partial = c)
    elif self.integer_partial:
      if '0' <= c <= '9':
        self.partial += c
        return False
      elif 'a' <= c <= 'z' or 'A' <= c <= 'Z':
        raise Scanner_error("The identifier '{}' on line {} starts with a number".format(
                              self.partial, self.line_number))
      else:
        return self.create_token('integer', c)
    elif self.identifier_partial:
      if 'a' <= c <= 'z' or 'A' <= c <= 'Z' or '0' <= c <= '9':
        self.partial += c
        return False
      elif self.partial in ['PROGRAM', 'BEGIN', 'END', 'CONST', 'TYPE', 'VAR', 'PROCEDURE',
                            'RETURN', 'ARRAY', 'OF', 'RECORD', 'DIV', 'MOD', 'IF', 'THEN',
                            'ELSE', 'REPEAT', 'UNTIL', 'WHILE', 'DO', 'WRITE', 'READ', 'INTEGER']:
        return self.create_token(set_partial = c)
      else:
        return self.create_token('identifier', c)
    else:
      raise Scanner_error("Urecognized symbol '{}' on line {}".format(self.partial, self.line_number))
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
          return self.partial_to_token()
        return False
      if c in [' ', '\f', '\r', '\t', '\n']:
        if c == '\n':
          self.line_number += 1
        if self.partial:
          return self.partial_to_token()
        continue
      if len(self.partial) >= 1:
        token = self.partial_to_token(c)
        if not token:
          continue
        return token
      if '0' <= c <= '9':
        self.integer_partial = True
      elif 'a' <= c <= 'z' or 'A' <= c <= 'Z':
        self.identifier_partial = True
      self.partial += c
    return False

