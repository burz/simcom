class Parser_error(Exception):
  def __init__(self, error):
    self.error = error
  def __str__(self):
    return "error: {}".format(self.error)

class Parser(object):
  def parse_tokens(self, tokens):
    self.tokens = tokens
    self.position = 0
    if not instructions = self.Program():
      raise Parser_error("There is not 'PROGRAM'")
    return Syntax_tree(instructions)
  def token(self):
    if self.position >= len(self.tokens):
      return False
    return self.tokens[self.position]
  def token_type(self):
    if self.position >= len(self.tokens):
      return False
    return self.tokens[self.position].token_type
  def token_line(self):
    if self.position >= len(self.tokens):
      return False
    return self.tokens[self.position].token_type
  def last(self):
    if self.position - 1 < 0 or self.position - 1 >= len(self.tokens):
      return False
    return self.tokens[self.position - 1]
  def last_type(self):
    if self.position - 1 < 0 or self.position - 1 >= len(self.tokens):
      return False
    return self.tokens[self.position - 1].token_type
  def last_line(self):
    if self.position - 1 < 0 or self.position - 1 >= len(self.tokens):
      return False
    return self.tokens[self.position - 1].line_number
  def next_token(self):
    self.position += 1
  def Program(self):
  def Declarations(self):
  def ConstDecl(self):
  def TypeDecl(self):
  def VarDecl(self):
  def ProcDecl(self):
  def Type(self):
  def Expression(self):
  def Term(self):
  def Factor(self):
  def Formals(self):
  def Formal(self):
  def Instructions(self):
  def Instruction(self):
  def Assign(self):
  def If(self):
  def Repeat(self):
  def While(self):
  def Condition(self):
  def Write(self):
  def Read(self):
  def Call(self):
  def Designator(self):
  def Selector(self):
    selectors = []
    while True:
      if self.token_type == '[':
        line_number = self.token_line()
        self.next_token()
        expr_list = self.ExpressionList()
        if not expr_list:
          raise Parser_error("The '[' on line {} is not followed by an ExpressionList".
                              format(line_number))
        if not self.token_type == ']':
          raise Parser_error("The '[' on line {} is not closed by a ']'".format(
                              line_number))
        self.next_token()
        selectors += expr_list
      elif self.token_type == '.':
        ident = self.identifier()
        if not ident:
          raise Parser_error("The '.' on line {} is not followed by an identifier".
                              format(self.last_line()))
        selectors += ident
      else:
        break
    return selectors
  def Actuals(self):
    return self.ExpressionList()
  def IdentifierList(self):
    ident = self.identifier()
    if not ident:
      return False
    identifiers = [ident]
    while self.token_type() == ',':
      self.next_token()
      ident = self.identifier()
      if not ident:
        raise Parser_error("The ',' on line {} is not followed by an identifier".format(
                           self.last_line()))
    return identifiers
  def ExpressionList(self):
    expression = self.Expression()
    if not expression:
      return False
    expressions = [expression]
    while self.token_type() == ',':
      self.next_token()
      expression = self.Expression()
      if not expression:
        raise Parser_error("The ',' on line {} is not followed by an expression".format(
                           self.last_line()))
    return expressions
  def identifier(self):
    if self.token_type() == "identifier":
      return True
    return False
  def integer(self):
    if self.current_token_type() == "integer":
      return True
    return False

