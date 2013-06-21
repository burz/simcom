import 'symbol_table'

negated_condition = { '=' : '#', '#' : '=', '<' : '>=', '>' : '<=', '<=' : '>', '>=' : '<' }

class Parser_error(Exception):
  def __init__(self, error):
    self.error = error
  def __str__(self):
    return "error: {}".format(self.error)

class Parser(object):
  def parse_tokens(self, tokens):
    self.tokens = tokens
    self.symbol_table = Symbol_table()
    self.position = 0
    if not instructions = self.Program():
      raise Parser_error("There is no 'PROGRAM' declared")
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
  def next_token(self):
    self.position += 1
  def type_check_binary_operation(self, operator, expression_left, expression_right):
    if not type(expression_left) is syntax_tree.Integer:
      raise Parser_error("The expression to the right of the '{}' on line {} is not an INTEGER".
                         format(operator, line))
    if not type(expression_right) is syntax_tree.Integer:
      raise Parser_error("The expression to the left of the '{}' on line {} is not an INTEGER".
                         format(operator, line))
  def Program(self):
  def Declarations(self):
  def ConstDecl(self):
  def TypeDecl(self):
  def VarDecl(self):
  def ProcDecl(self):
  def Type(self):
  def Expression(self):
  def Term(self):
    starting_position = self.position
    expression_left = self.Factor()
    if not expression_left:
      return False
    if not self.token_type() in ['*', 'DIV', 'MOD']:
      self.position = starting_position
      return False
    line = self.token_line()
    operator = self.token().data
    self.next_token()
    expression_right = self.Factor()
    if not expression_right:
      raise Parser_error("The '{}' on line {} is not followed by a Factor".format(operator, line))
    type_check_binary_operation(operator, expression_left, expression_right, line)
    binary = syntax_tree.Binary(operator, expression_left, expression_right, line)
    return syntax_tree.Expression(binary, self.symbol_table.integer_singleton, binary.line)
  def Factor(self):
    integer = self.integer()
    if integer:
      return integer
    designator = self.Designator()
    if designator:
      return syntax_tree.Expression(designator, designator.type_object ,designator.line)
    if self.token_type() == '(':
      line = self.token_line()
      self.next_token()
      expression = self.Expression()
      if not expression:
        raise Parser_error("The '(' on line {} is not followed by an Expression".format(line))
      if not self.token_type() == ')':
        raise Parser_error("The '(' on line {} is not terminated by a ')'".format(line))
      return expression
    call = self.Call()
    if call:
      return syntax_tree.Expression(call, call.type_object, call.line)
    return False
  def Instructions(self):
    instruction = self.Instruction()
    if not instruction:
      return False
    instructions = [instruction]
    while self.token_type() == ';':
      line = self.token_line()
      self.next_token()
      instruction = self.Instruction()
      if not instruction:
        raise Parse_error("The ';' on line {} is not followed by any instructions".format(line))
      instructions.append(instruction)
    return syntax_tree.Instructions(instructions, instructions[0].line)
  def Instruction(self):
    return self.Assign() or self.If() or self.Repeat() or self.While() or self.Read() or
           self.Write() or self.Call()
  def Assign(self):
    starting_position = self.position
    designator = self.Designator()
    if not designator:
      return False
    if not self.token_type() == ':=':
      self.position = starting_position
      return False
    line = self.token_line()
    self.next_token()
    expression = self.Expression()
    if not expression:
      raise Parser_error("The ':=' on line {} is not followed by an Expression".format(line))
    if not type(location.type_object) is type(location.type_object):
      raise Parser_error("The types of the location and expression for ':=' on line {} do not match".
                         format(line))
    return syntax_tree.Assign(designator, expression, line)
  def If(self):
    if not self.token_type() == 'IF':
      return False
    line = self.token_line()
    self.next_token()
    condition = self.Condition()
    if not condition:
      raise Parser_error("The 'IF' on line {} is not followed by a Condition".format(line))
    if not self.token_type() == 'THEN':
      raise Parser_error("The 'IF' on line {} is not followed by a 'THEN'".format(line))
    then_line = self.token_line()
    self.next_token()
    instructions_true = self.Instructions()
    if not instructions_true:
      raise Parser_error("The 'THEN' on line {} is not followed by any Instructions".format(
                         then_line))
    instructions_false = False
    if self.token_type() == 'ELSE':
      else_line = self.token_line()
      self.next_token()
      instructions_false = self.Instructions()
      if not instructions_false:
        raise Parser_error("The 'ELSE' on line {} is not followed by any Instructions".format(
                           else_line))
    if not self.token_type() == 'END':
      raise Parser_exception("The 'IF' on line {} is not followed by an 'END'".format(line))
    self.next_token()
    return syntax_tree.If(condition, instructions_true, instructions_false, line)
  def Repeat(self):
    if not self.token_type() == 'REPEAT':
      return False
    line = self.token_line()
    self.next_token()
    instructions = self.Instructions()
    if not instructions:
      raise Parser_error("The 'REPEAT' on line {} is not followed by any Instructions".format(line))
    if not self.token_type() == 'UNTIL':
      raise Parser_error("The 'REPEAT' on line {} is not followed by an 'UNTIL'".format(line))
    until_line = self.token_line()
    self.next_token()
    condition = self.Condition()
    if not condition:
      raise Parser_error("The 'UNTIL' on line {} is not followed by a Condition".format(until_line))
    if not self.token_type() == 'END':
      raise Parser_error("The 'REPEAT' on line {} is not terminated by an 'END'".format(line))
    self.next_token()
    return syntax_tree.Repeat(condition, instructions, line)
  def While(self):
    if not self.token_type() == 'WHILE':
      return False
    line = self.token_line()
    self.next_token()
    condition = self.Condition()
    if not condition:
      raise Parser_error("The 'WHILE' on line {} is not followed by a Condition".format(line))
    if not self.token_type() == 'DO':
      raise Parser_error("The 'WHILE' on line {} is not followed by a 'DO'".format(line))
    do_line = self.token_line()
    self.next_token()
    instructions = self.Instructions()
    if not instructions:
      raise Parser_error("The 'DO' on line {} is not followed by any Instructions".format(do_line))
    if not self.token_type() == 'END':
      raise Parser_error("The 'WHILE' on line {} is not teminated by an 'END'".format(line))
    repeat_relation = negated_relation[condition.relation]
    repeat_condition = syntax_tree.Condition(repeat_relation, condition.expression_right,
                                             condition.expression_right, condition.line)
    repeat = syntax_tree.Repeat(repeat_condition, instructions, repeat_condition.line)
    instruction = syntax_tree.Instruction(repeat, repeat.line)
    instructions = syntax_tree.Instructions([instruction], instruction.line)
    return syntax_tree.If(condition, instructions False, line)
  def Condition(self):
    starting_position = self.position
    expression_left = self.Expression()
    if not expression_left:
      return False
    relation = self.token()
    if not relation in ['=', '#', '<', '>', '<=', '>=']:
      self.position = starting_position
      return False
    expression_right = self.Expression()
    if not expression_right:
      raise Parser_error("There is no Expression following the '{}' on line {}".format(
                         operator.data, operator.line))
    return syntax_tree.Condition(relation, expression_left, expression_right, line)
  def Write(self):
    if not self.token_type() == 'WRITE':
      return False
    line = self.token_line()
    self.next_token()
    expression = self.Expression()
    if not expression:
      raise Parser_error("The 'WRITE' on line {} is not followed by an Expression".format(line))
    if not type(expression.type_object) is self.symbol_tree.integer_singleton:
      raise Parser_error("The Expression on line {} must result in an INTEGER".format(
                         expression.line))
    return syntax_tree.Write(expression, line)
  def Read(self):
    if not self.token_type == 'READ':
      return False
    line = self.token_line()
    self.next_token()
    designator = self.Designator()
    if not designator:
      raise Parser_error("The 'READ' on line {} is not followed by a Designator".format(line))
    return syntax_tree.Read(designator, line)
  def Call(self):
    starting_position = self.position
    identifier = self.identifier()
    if not identifier:
      return False
    definition = self.symbol_table.find(identifier.data)
    if not self.token_type == '(' or not type(definition) is symbol_tree.Procedure:
      self.position = starting_position
      return False
    line = self.token_line()
    self.next_token()
    actuals = self.Actuals()
    if not self.token_type == ')':
      raise Parser_error("The '(' on line {} is not terminated by a ')'".format(line))
    self.next_token()
    return syntax_tree.Call(definition, actual_expressions, definition.type_object, identifier.line)
  def Designator(self):
    identifier = self.identifier()
    if not identifier:
      return False
    table_entry = self.symbol_table.find(identifier.data)
    if not table_entry:
      raise Parse_error("The identifier '{}' on line {} has not been defined".format(
                         identifier.data, identifier.line))
    selectors = self.Selector()
    variable = syntax_tree.Variable(identifier.data, table_entry, identifier.line)
    location = syntax_tree.Location(variable, variable.line)
    for selector in selectors:
      if type(location.child) == syntax_tree.Variable
        definition = location.child.table_entry
      else:
        definition = location.child.type_object
      if type(selector) is symbol_table.Expression:
        if not type(definition) is symbol_table.Array:
          raise Parse_error("The index on line {} does not follow an Array".format(selector.line))
        index = syntax_tree.Index(location, expression, definition.type_object, expression.line)
        location = syntax_tree.Location(index, index.line)
      else:
        if not type(definition) is symbol_table.Record:
          raise Parse_error("The field '{}' on line {} does not follow a Record".format(
                            selector.data, selector.line))
        table_entry = definition.scope.find(selector.data)
        if not table_entry:
          return Parse_error("The field '{}' on line {} has not been defined".format(
                             selector.data, selector.line))
        variable = Variable(selector.data, table_entry, selector.line)
        field = syntax_tree.Field(location, variable, table_entry, variable.line)
        location = syntax_tree.Location(field, field.line)
    return location
  def Formals(self):
    formal = self.Formal()
    if not formal:
      return False
    formals = []
    formals += formal
    while self.token_type() == ';':
      line = self.token_line()
      self.next_token()
      formal = self.Formal()
      if not formal:
        raise Parser_error("The ';' on line {} is not followed by a Formal".format(line)
      formals += formal
    return formals
  def Formal(self):
    line = self.token_line()
    identifiers = self.IdentifierList()
    if not identifiers:
      return False
    if not self.token_type() == ':':
      raise Parser_error("The IdentifierList on line {} is not followed by a ':'".format(line))
    line = self.token_line()
    self.next_token()
    type_object = self.Type()
    if not type_object:
      raise Parser_error("The ':' on line {} is not followed by a Type".format(line))
    definitions = []
    for identifier in identifiers:
      self.symbol_table.insert(identifier.data, type_object)
      definitions.append(identifier.data)
    return definitions
  def Actuals(self):
    return self.ExpressionList()
  def Selector(self):
    selectors = []
    while True:
      if self.token_type == '[':
        line = self.token_line()
        self.next_token()
        expr_list = self.ExpressionList()
        if not expr_list:
          raise Parser_error("The '[' on line {} is not followed by an ExpressionList".format(line))
        if not self.token_type == ']':
          raise Parser_error("The '[' on line {} is not closed by a ']'".format(line))
        self.next_token()
        selectors += expr_list
      elif self.token_type == '.':
        self.next_token()
        identifier = self.identifier()
        if not identifier:
          raise Parser_error("The '.' on line {} is not followed by an identifier".format(
                             self.last_line()))
        selectors.append(identifier)
      else:
        break
    return selectors
  def IdentifierList(self):
    identifier = self.identifier()
    if not identifier:
      return False
    identifiers = [identifier]
    while self.token_type() == ',':
      self.next_token()
      identifier = self.identifier()
      if not identifier:
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
    if not self.token_type() == "integer":
      return False
    constant = symbol_table.Constant(self.symbol_table.integer_singleton, self.token().data,
                                     self.token_line)
    number = syntax_tree.Number(constant, constant.line)
    return syntax_tree.Expression(number, constant.type_object ,number.line)

