import sys

class Token(object):
  def __init__(self, symbol_type, data, line_number):
    self.symbol_type = symbol_type
    self.data = data
    self.line_number = line_number
  def __repr__(self):
    if self.symbol_type in ['integer', 'identifier']:
      return "{}<{}>@{}".format(self.symbol_type, self.data, self.line_number)
    else:
      return "{}@{}".format(self.token_type)

class Scan_error(Exception):
  def __init__(self, error):
    self.error = error
  def __str__(self):
    return 'error: ' + self.error

class Scanner(object):
  def __init__(self, filename = False):
    self.file_input = (len(filename) == 0)
    if not filename:
      try:
        self.stream = open(filename, 'r')
      except IOError:
        raise Scan_error("Could not open '{}'".format(filename))
    self.string_buffer = ""

  def reset_buffer(self):
    self.integer_buffer = False
