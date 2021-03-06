import symbol_table
import syntax_tree
import interpreter

negated_relation = { '=' : '#', '#' : '=', '<' : '>=', '>' : '<=', '<=' : '>', '>=' : '<' }

class Parser_error(Exception):
  def __init__(self, error):
    self.error = error
  def __str__(self):
    return "error: {}".format(self.error)

class Parser(object):
  def parse_tokens(self, tokens):
    self.tokens = tokens
    self.symbol_table = symbol_table.Symbol_table()
    self.position = 0
    self.in_expression = 0
    instructions = self.Program()
    if not instructions:
      raise Parser_error("There is no 'PROGRAM' declared")
    return instructions, self.symbol_table
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
    return self.tokens[self.position].line
  def next_token(self):
    self.position += 1
  def type_check_binary_operation(self, operator, expression_left, expression_right, line):
    if not type(expression_right.type_object) in [symbol_table.Integer, symbol_table.Constant]:
      raise Parser_error("The expression to the left of the '{}' on line {} is not an INTEGER".
                         format(operator, line))
    if not type(expression_left.type_object) in [symbol_table.Integer, symbol_table.Constant]:
      raise Parser_error("The expression to the right of the '{}' on line {} is not an INTEGER".
                         format(operator, line))
  def Program(self):
    if not self.token_type() == 'PROGRAM':
      return False
    line = self.token_line()
    self.next_token()
    identifier = self.identifier()
    if not identifier:
      raise Parser_error("The 'PROGRAM' on line {} is not followed by an identifier".format(line))
    if not self.token_type() == ';':
      raise Parser_error("PROGRAM '{}' on line {} is not followed by a ';'".format(
                         identifier.data, identifier.line))
    self.next_token()
    self.Declarations()
    instructions = False
    if self.token_type() == 'BEGIN':
      begin_line = self.token_line()
      self.next_token()
      instructions = self.Instructions()
      if not instructions:
        raise Parser_error("The 'BEGIN' on line {} is not followed by any Instructions".format(
                           begin_line))
    if not self.token_type() == 'END':
      raise Parser_error("The 'PROGRAM' on line {} is not terminated by an 'END'".format(line))
    end_line = self.token_line()
    self.next_token()
    final_id = self.identifier()
    if not final_id:
      raise Parser_error("The 'END' on line {} is not followed by a program name to close".format(
                         end_line))
    if not final_id.data == identifier.data:
      raise Parser_error(
             "The name of the program on line {} does not match the name of it's closing on line {}".
                format(identifier.line, final_id.line))
    if not self.token_type() == '.':
      raise Parser_error("The program closing on line {} is not followed by a '.'".format(end_line))
    self.next_token()
    return syntax_tree.Syntax_tree(instructions)
  def Declarations(self):
    self.in_procedure = False
    self.forward_declarations = {}
    self.call_type_checks = []
    self.argument_number_checks = []
    while self.ConstDecl() or self.TypeDecl() or self.VarDecl() or self.ProcDecl():
      pass
    if self.forward_declarations:
      error = ''
      for name, call in self.forward_declarations:
        error += "       The function '{}' on line {} has not been defined\n".format(name, call.line)
      raise Parser_error(error[7:-1])
    for check in self.call_type_checks:
      if not type(check.type_object) is symbol_table.Integer:
        raise Parser_error("The call to '{}' on line {} must result in an INTEGER".format(
                             check.definition.name, check.line))
  def ConstDecl(self):
    if not self.token_type() == 'CONST':
      return False
    self.next_token()
    while True:
      identifier = self.identifier()
      if not identifier:
        return True
      if not self.token_type() == '=':
        raise Parser_error("The constant declaration of '{}' on line {} is not followed by a '='".
                            format(identifier.data, identifier.line))
      self.next_token()
      expression = self.Expression()
      if not expression:
        raise Parser_error(
                "The constant declaration of '{}' on line {} is not followed by an Expression".
                  format(identifier.data, identifier.line))
      if not type(expression.type_object) is symbol_table.Integer:
        raise Parser_error(
            "The expression following the constant declaration of '{}' on line {} is not an INTEGER".
               format(identifier.data, identifier.line))
      value = interpreter.Interpreter.evaluate_expression(interpreter.Interpreter(), expression)
      if not self.token_type() == ';':
        raise Parser_error("The constant declaration of '{}' on line {} is not followed by a ';'".
                             format(identifier.data, identifier.line))
      self.next_token()
      constant = symbol_table.Constant(self.symbol_table.integer_singleton, value, expression.line)
      if not self.symbol_table.insert(identifier.data, constant):
        previous_definition = self.symbol_table.find(identifier.data)
        raise Parser_error("The constant delaration of '{}' on line {} ".format(
                             identifier.data, identifier.line) +
                           "conflicts with the previous declaration on line {}".format(
                             previous_definition.line))
    return True
  def TypeDecl(self):
    if not self.token_type() == 'TYPE':
      return False
    self.next_token()
    while True:
      identifier = self.identifier()
      if not identifier:
        return True
      if not self.token_type() == '=':
        raise Parser_error("The type declaration of '{}' on line {} is not followed by a '='".
                             format(identifier.data, identifier.line))
      self.next_token()
      type_object = self.Type()
      if not type_object:
        raise Parser_error("The type declaration of '{}' on line {} is not followed by a Type".
                             format(identifier.data, identifier.line))
      if not self.token_type() == ';':
        raise Parser_error("The type declaration of '{}' on line {} is not followed by a ';'".
                             format(identifier.data, identifier.line))
      self.next_token()
      if not self.symbol_table.insert(identifier.data, type_object):
        previous_definition = self.symbol_table.find(identifier.data)
        raise Parser_error(
         "The type delaration of '{}' on line {} conflicts with the previous declaration on line {}".
            format(identifier.data, identifier.line, previous_definition.line))
    return True
  def VarDecl(self):
    if not self.token_type() == 'VAR':
      return False
    self.next_token()
    while True:
      identifiers = self.IdentifierList()
      if not identifiers:
        return True
      if not self.token_type() == ':':
        if len(identifiers) is 1:
          raise Parser_error("The variable declaration of '{}' on line {} is not followed by a ':'".
                               format(identifiers[0].data, identifiers[0].line))
        else:
          error = "The variable declarations of:\n"
          for identifier in identifiers:
            error += "         '{}' on line '{}'\n".format(identifier.data, identifier.line)
          raise Parser_error(error + "       are not follwed by a ':'")
      self.next_token()
      type_object = self.Type()
      if not type_object:
        if len(identifiers) is 1:
          raise Parser_error("The variable declaration of '{}' on line {} is not followed by a Type".
                               format(identifiers[0].data, identifiers[0].line))
        else:
          error = "The variable declarations of:\n"
          for identifier in identifiers:
            error += "         '{}' on line '{}'\n".format(identifier.data, identifier.line)
          raise Parser_error(error + "       are not follwed by a Type")
      if not self.token_type() == ';':
        if len(identifiers) is 1:
          raise Parser_error("The variable declaration of '{}' on line {} is not followed by a ';'".
                               format(identifiers[0].data, identifiers[0].line))
        else:
          error = "The variable declarations of:\n"
          for identifier in identifiers:
            error += "         '{}' on line '{}'\n".format(identifier.data, identifier.line)
          raise Parser_error(error + "       are not follwed by a ';'")
      self.next_token()
      for identifier in identifiers:
        if not self.symbol_table.insert(identifier.data, type_object):
          previous_definition = self.symbol_table.find(identifier.data)
          raise Parser_error("The variable declaration of '{}' on line {} ".format(
                               identifier.data, identifier.line) +
                             "conflicts with the previous declaration at {}".format(
                               previous_definition.line))
    return True
  def ProcDecl(self):
    if not self.token_type() == 'PROCEDURE':
      return False
    self.in_procedure = True
    line = self.token_line()
    self.next_token()
    identifier = self.identifier()
    if not identifier:
      raise Parser_error("The 'PROCEDURE' on line {} is not followed by an identifier".format(line)) 
    if not self.token_type() == '(':
      raise Parser_error("The procedure declaration of '{}' on line {} is not followed by a '('".
                           format(identifier.data, line))
    par_line = self.token_line()
    self.next_token()
    self.symbol_table.push_scope()
    formals = self.Formals()
    if not self.token_type() == ')':
      raise Parser_error("The '(' on line {} is not terminated by a ')'".format(par_line))
    self.next_token()
    return_type_object = False
    if self.token_type() == ':':
      return_type_line = self.token_line()
      self.next_token()
      return_type_object = self.Type()
      if not return_type_object:
        raise Parser_error("The ':' on line {} is not followed by a Type".format(return_type_line))
    if not self.token_type() == ';':
      raise Parser_error("The procedure declaration of '{}' on line {} is not followed by a ';'".
                           format(identifier.data, line))
    self.next_token()
    while self.VarDecl():
      pass
    instructions = False
    if self.token_type() == 'BEGIN':
      begin_line = self.token_line()
      self.next_token()
      instructions = self.Instructions()
      if not instructions:
        raise Parser_error("The 'BEGIN' on line {} is not followed by any Instructions".format(
                             begin_line))
    return_expression = False
    return_line = False
    if self.token_type() == 'RETURN':
      return_line = self.token_line()
      self.next_token()
      return_expression = self.Expression()
      if not return_expression:
        raise Parser_error("The 'RETURN' on line {} is not followed by an Expression".format(
                             return_line))
      if not return_expression.type_object is return_type_object:
        raise Parser_error(
                "The return type defined for '{}' on line {} does not match the type of the".
                  format(identifier.data, line) +
                "return expression on line {}".format(return_line))
    elif return_type_object:
      raise Parser_error(
              "Expected a return statement in the procedure declaration of '{}' on line {}".
                format(identifier.data, line))
    if not self.token_type() == 'END':
      raise Parser_error("The procedure declaration of '{}' on line {} is not followed by an 'END'".
                           format(identifier.data, line))
    end_line = self.token_line()
    self.next_token()
    closing_name = self.identifier()
    if not closing_name:
      raise Parser_error("The 'END' on line {} is not followed by a procedure name to close".format(
                           end_line))
    if not closing_name.data == identifier.data:
      raise Parser_error("Expected a closing of procedure '{}'; got '{}' on line {}".format(
                           identifier.data, closing_name.data, closing_name.line))
    if not self.token_type() == ';':
      raise Parser_error("Expected a ';' following the closing of the procedure '{}' on line {}".
                           format(closing_name.data, closing_name.line))
    self.next_token()
    scope = self.symbol_table.pop_scope()
    procedure = symbol_table.Procedure(identifier.data, formals, scope, return_type_object,
                                       instructions, return_expression, line)
    if not self.symbol_table.insert(identifier.data, procedure):
      previous_definition = self.symbol_table.find(identifier.data)
      raise Parser_error("The procedure definition of '{}' on line {} ".format(
                           identifier.data, line) +
                         "conflicts with the previous declaration on line {}".format(
                           previous_definition.line))
    self.in_procedure = False
    if self.forward_declarations:
      delete = []
      for name, calls in self.forward_declarations.iteritems():
        if name == identifier.data:
          for call in calls:
            call.definition = procedure
            call.type_object = return_type_object
          delete.append(name)
      for name in delete:
        del self.forward_declarations[name]
    return True
  def Type(self):
    identifier = self.identifier()
    if identifier:
      definition = self.symbol_table.find(identifier.data)
      if not type(definition) in [symbol_table.Integer, symbol_table.Array, symbol_table.Record]:
        raise Parser_error("The identifier '{}' on line {} does not name a type".format(
                           identifier.data, identifier.line))
      return definition
    if self.token_type() == 'ARRAY':
      line = self.token_line()
      self.next_token()
      expression = self.Expression()
      if not expression:
        raise Parser_error("The 'ARRAY' on line {} is not followed by an Expression".format(line))
      if not type(expression.type_object) is symbol_table.Integer:
        raise Parser_error("The Expression following the 'ARRAY' on line {} must be an INTEGER".
                             format(expression.line))
      size = interpreter.Interpreter.evaluate_expression(interpreter.Interpreter(), expression)
      if not self.token_type() == 'OF':
        raise Parser_error("The 'ARRAY' on line {} is not followed by a 'OF'".format(line))
      of_line = self.token_line()
      self.next_token()
      type_object = self.Type()
      if not type_object:
        raise Parser_error("The 'OF' on line {} is not followed by a Type".format(of_line))
      return symbol_table.Array(type_object, size, line)
    if self.token_type() == 'RECORD':
      line = self.token_line()
      self.next_token()
      self.symbol_table.push_scope()
      while True:
        identifiers = self.IdentifierList()
        if not identifiers:
          break
        if not self.token_type() == ':':
          raise Parser_error(
                  "The IdentifierList following the 'RECORD' on line {} is not followed by a ':'".
                    format(identifiers[0].line))
        col_line = self.token_line()
        self.next_token()
        type_object = self.Type()
        if not type_object:
          raise Parser_error("The ':' on line {} is not followed by a Type".format(col_line))
        if not self.token_type() == ';':
          raise Parser_error("The field declarations on line {} are not followed by a ';'".
                               format(col_line))
        self.next_token()
        for ident in identifiers:
          if not self.symbol_table.insert(ident.data, type_object):
            previous_definition = self.symbol_table.find(ident.data)
            raise Parser_error(
                    "The definition of '{}' on line {} conflicts with the previous definition at {}".
                      format(ident.data, ident.line, previous_definition.line))
      if not self.token_type() == 'END':
        raise Parser_error(
                "The definition of the 'RECORD' on line {} was not terminated by an 'END'".
                  format(line))
      self.next_token()
      scope = self.symbol_table.pop_scope()
      return symbol_table.Record(scope, line)
    return False
  def Expression(self):
    self.in_expression += 1
    if self.token_type() == '+':
      line = self.token_line()
      self.next_token()
      term = self.Term()
      if not term:
        raise Parser_error("The '+' on line {} is not followed by a Term".format(line))
    elif self.token_type() == '-':
      line = self.token_line()
      self.next_token()
      term = self.Term()
      if not term:
        raise Parser_error("The '-' on line {} is not followed by a Term".format(line))
      constant = symbol_table.Constant(self.symbol_table.integer_singleton, 0, line)
      number = syntax_tree.Number(constant, constant.line)
      expression = syntax_tree.Expression(number, constant.type_object, number.line)
      self.type_check_binary_operation('-', expression, term, line)
      binary = syntax_tree.Binary('-', expression, term, line)
      term = syntax_tree.Expression(binary, constant.type_object, binary.line)
    else:
      line = self.token_line
      term = self.Term()
      if not term:
        self.in_expression -= 1
        return False
    while self.token_type() in ['+', '-']:
      op_line = self.token_line()
      operator = self.token_type()
      self.next_token()
      new_term = self.Term()
      if not new_term:
        raise Parser_error("The '{}' on line {} is not followed by a Term".format(operator, op_line))
      self.type_check_binary_operation(operator, term, new_term, op_line)
      if type(term.child) is syntax_tree.Number and type(new_term.child) is syntax_tree.Number:
        interp = interpreter.Interpreter()
        term_result = interp.evaluate_expression(term)
        new_term_result = interp.evaluate_expression(new_term)
        if operator == '+':
          result = term_result + new_term_result
        else: # -
          result = term_result - new_term_result
        constant = symbol_table.Constant(self.symbol_table.integer_singleton, result, op_line)
        child = syntax_tree.Number(constant, constant.line)
      else:
        child = syntax_tree.Binary(operator, term, new_term, op_line)
      term = syntax_tree.Expression(child, self.symbol_table.integer_singleton, child.line)
    self.in_expression -= 1
    return term
  def Term(self):
    factor = self.Factor()
    if not factor:
      return False
    while self.token_type() in ['*', 'DIV', 'MOD']:
      line = self.token_line()
      operator = self.token_type()
      self.next_token()
      new_factor = self.Factor()
      if not new_factor:
        raise Parser_error("The '{}' on line {} is not followed by a Factor".format(operator, line))
      self.type_check_binary_operation(operator, factor, new_factor, line)
      if type(factor.child) is syntax_tree.Number and type(new_factor.child) is syntax_tree.Number:
        interp = interpreter.Interpreter()
        factor_result = interp.evaluate_expression(factor)
        new_factor_result = interp.evaluate_expression(new_factor)
        if operator == '*':
          result = factor_result * new_factor_result
        elif operator == 'DIV':
          if new_factor_result is 0:
            raise Parser_error("The right side of the 'DIV' on line {} evaluated to 0".format(line))
          result = factor_result / new_factor_result
        else: # MOD
          if new_factor_result is 0:
            raise Parser_error("The right side of the 'MOD' on line {} evaluated to 0".format(line))
          result = factor_result % new_factor_result
        constant = symbol_table.Constant(self.symbol_table.integer_singleton, result, line)
        child = syntax_tree.Number(constant, constant.line)
      else:
        child = syntax_tree.Binary(operator, factor, new_factor, line)
      factor = syntax_tree.Expression(child, self.symbol_table.integer_singleton, child.line)
    return factor
  def Factor(self):
    integer = self.integer()
    if integer:
      return integer
    designator = self.Designator()
    if designator:
      if type(designator) is syntax_tree.Number:
        return syntax_tree.Expression(designator, self.symbol_table.integer_singleton,
                                      designator.line)
      return syntax_tree.Expression(designator, designator.type_object, designator.line)
    if self.token_type() == '(':
      line = self.token_line()
      self.next_token()
      expression = self.Expression()
      if not expression:
        raise Parser_error("The '(' on line {} is not followed by an Expression".format(line))
      if not self.token_type() == ')':
        raise Parser_error("The '(' on line {} is not terminated by a ')'".format(line))
      self.next_token()
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
        raise Parser_error("The ';' on line {} is not followed by any instructions".format(line))
      instructions.append(instruction)
    return syntax_tree.Instructions(instructions, instructions[0].line)
  def Instruction(self):
    instruction = (self.Assign() or self.If() or self.Repeat() or self.While() or self.Read() or
                   self.Write() or self.Call())
    if not instruction:
      return False
    return syntax_tree.Instruction(instruction, instruction.line)
  def Assign(self):
    starting_position = self.position
    location = self.Designator()
    if not location:
      return False
    if not self.token_type() == ':=':
      self.position = starting_position
      return False
    line = self.token_line()
    self.next_token()
    expression = self.Expression()
    if not expression:
      raise Parser_error("The ':=' on line {} is not followed by an Expression".format(line))
    if not type(location.type_object) is type(expression.type_object):
      raise Parser_error("The types of the location and expression for ':=' on line {} do not match".
                         format(line))
    return syntax_tree.Assign(location, expression, line)
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
    self.next_token()
    repeat_relation = negated_relation[condition.relation]
    repeat_condition = syntax_tree.Condition(repeat_relation, condition.expression_left,
                                             condition.expression_right, condition.line)
    repeat = syntax_tree.Repeat(repeat_condition, instructions, repeat_condition.line)
    instruction = syntax_tree.Instruction(repeat, repeat.line)
    instructions = syntax_tree.Instructions([instruction], instruction.line)
    return syntax_tree.If(condition, instructions, False, line)
  def Condition(self):
    starting_position = self.position
    expression_left = self.Expression()
    if not expression_left:
      return False
    relation = self.token()
    if not relation.data in ['=', '#', '<', '>', '<=', '>=']:
      self.position = starting_position
      return False
    self.next_token()
    expression_right = self.Expression()
    if not expression_right:
      raise Parser_error("There is no Expression following the '{}' on line {}".format(
                         operator.data, operator.line))
    self.type_check_binary_operation(relation.data, expression_left, expression_right, relation.line)
    return syntax_tree.Condition(relation.data, expression_left, expression_right, relation.line)
  def Write(self):
    if not self.token_type() == 'WRITE':
      return False
    line = self.token_line()
    self.next_token()
    expression = self.Expression()
    if not expression:
      raise Parser_error("The 'WRITE' on line {} is not followed by an Expression".format(line))
    if not type(expression.type_object) is symbol_table.Integer:
      raise Parser_error("The Expression on line {} must result in an INTEGER".format(
                         expression.line))
    return syntax_tree.Write(expression, line)
  def Read(self):
    if not self.token_type() == 'READ':
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
    if not self.token_type() == '(':
      self.position = starting_position
      return False
    forward = False
    if not definition:
      if not self.in_procedure:
        raise Parser_error("The Procedure '{}' on line {} has not been defined".format(
                             identifier.data, identifier.line))
      forward = True
    elif not type(definition) is symbol_table.Procedure:
      raise Parser_error("'{}' on line {} is not a Procedure".format(
                           identifier.data, identifier.line))
    line = self.token_line()
    self.next_token()
    actuals = self.Actuals()
    if forward:
      if self.in_expression:
        return_type = self.symbol_table.integer_singleton
      else:
        return_type = False
    else:
      return_type = definition.type_object
    call = syntax_tree.Call(definition, actuals, return_type, identifier.line)
    if not forward:
      length = len(actuals) if actuals else 0
      definition_length = len(definition.formals) if definition.formals else 0
      if length != definition_length:
        raise Parser_error(
             "The call to '{}' on line {} does not have the correct number of arguments ({} for {})".
                  format(identifier.data, identifier.line, length, definition_length))
    else:
      self.argument_number_checks.append(call)
      if not identifier.data in self.forward_declarations:
        self.forward_declarations[identifier.data] = [call]
      else:
        self.forward_declarations[identifier.data].append(call)
      if self.in_expression:
        self.call_type_checks.append(call)
    if not self.token_type() == ')':
      raise Parser_error("The '(' on line {} is not terminated by a ')'".format(line))
    self.next_token()
    return call
  def Designator(self):
    starting_position = self.position
    identifier = self.identifier()
    if not identifier:
      return False
    if self.token_type() == '(':
      self.position = starting_position
      return False
    table_entry = self.symbol_table.find(identifier.data)
    if not table_entry:
      self.position = starting_position
      return False
    if type(table_entry) is symbol_table.Constant:
      return syntax_tree.Number(table_entry, identifier.line)
    selectors = self.Selector()
    variable = syntax_tree.Variable(identifier.data, table_entry, identifier.line)
    location = syntax_tree.Location(variable, table_entry, variable.line)
    for selector in selectors:
      if type(location.child) == syntax_tree.Variable:
        definition = location.child.table_entry
      else:
        definition = location.child.type_object
      if type(selector) is syntax_tree.Expression:
        if not type(definition) is symbol_table.Array:
          raise Parser_error("The index on line {} does not follow an Array".format(selector.line))
        index = syntax_tree.Index(location, selector, definition.type_object, selector.line)
        location = syntax_tree.Location(index, index.type_object, index.line)
      else:
        if not type(definition) is symbol_table.Record:
          raise Parser_error("The field '{}' on line {} does not follow a Record".format(
                            selector.data, selector.line))
        table_entry = definition.scope.find(selector.data)
        if not table_entry:
          raise Parser_error("The field '{}' on line {} has not been defined".format(
                             selector.data, selector.line))
        variable = syntax_tree.Variable(selector.data, table_entry, selector.line)
        field = syntax_tree.Field(location, variable, table_entry, variable.line)
        location = syntax_tree.Location(field, table_entry, field.line)
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
        raise Parser_error("The ';' on line {} is not followed by a Formal".format(line))
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
      if self.token_type() == '[':
        line = self.token_line()
        self.next_token()
        expr_list = self.ExpressionList()
        if not expr_list:
          raise Parser_error("The '[' on line {} is not followed by an ExpressionList".format(line))
        if not self.token_type() == ']':
          raise Parser_error("The '[' on line {} is not closed by a ']'".format(line))
        self.next_token()
        selectors += expr_list
      elif self.token_type() == '.':
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
      identifiers.append(identifier)
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
      expressions.append(expression)
    return expressions
  def identifier(self):
    if not self.token_type() == 'identifier':
      return False
    identifier = self.token()
    self.next_token()
    return identifier
  def integer(self):
    if not self.token_type() == 'integer':
      return False
    constant = symbol_table.Constant(self.symbol_table.integer_singleton, int(self.token().data),
                                     self.token_line())
    number = syntax_tree.Number(constant, constant.line)
    self.next_token()
    return syntax_tree.Expression(number, constant.type_object, number.line)

