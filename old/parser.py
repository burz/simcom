import scanner
import symbol_table
import ast

class Parse_exception(Exception):
  def __init__(self, error):
    self.error = error
  def __str__(self):
    return "error: " + self.error

class Parser(object):
  def __init__(self, tokens, graphical = False, create_symbol_table = True, ast = True):
    """Create a Parser

    tokens := Tokens from a Scanner
    graphical := the Parser should create a graphical tree
    create_symbol_table := a symbol table should be created
    ast := an abstract syntax tress should be created

    """
    self.tokens = tokens
    self.graphical = graphical
    if graphical:
      self.stack = []
      self.number = 0
    self.create_symbol_table = create_symbol_table
    self.create_ast = ast
    if ast:
      self.create_symbol_table = True
    if create_symbol_table:
      self.table = symbol_table.Symbol_table()
      self.identifiers = []
    self.position = 0
    self.current_depth = 0
    self.tree = []
    self.parsing_definitions = False
    self.forward_declarations = []
    self.type_checks = []
    self.integer_returns = []
  def _remove_from_tree(self):
    self.tree.pop()
    if self.graphical:
      self.tree.pop()
      self.stack.pop()
      self.number -= 1
  def _get_position(self):
    return self.tokens[self.position].start_position, self.tokens[self.position].end_position
  def _get_last_position(self):
    return self.tokens[self.position - 1].start_position, self.tokens[self.position - 1].end_position
  def _token_position(self):
    return self.tokens[self.position].start_position
  def _token_type(self):
    return self.tokens[self.position].token_type
  def _last_token_type(self):
    return self.tokens[self.position - 1].token_type
  def _get_token(self):
    return  self.tokens[self.position]
  def _get_last_token(self):
    return self.tokens[self.position - 1]
  def _get_parent(self):
    if len(self.stack) == 0:
      return -1
    while self.stack[len(self.stack) - 1][1] >= self.current_depth:
      self.stack.pop()
      if len(self.stack) == 0:
        return -1
    return self.stack[len(self.stack) - 1][0]
  def _add_token(self):
    if not self.graphical:
      self.tree.append((False, self.tokens[self.position], self.current_depth))
    else:
      label = "L" + str(self.number)
      self.number += 1
      if self.tokens[self.position].token_type == "integer":
        self.tree.append("{} [label=\"{}\",shape=diamond]".format(label, str(self.tokens[self.position].data)))
      else:
        self.tree.append("{} [label=\"{}\",shape=diamond]".format(label, self.tokens[self.position].data))
      last = self._get_parent()
      if not last == -1:
        self.tree.append("{} -> {}".format(last, label))
    self.position += 1
  def _add_non_terminal(self, string):
    if not self.graphical:
      self.tree.append((True, string, self.current_depth))
    else:
      label = "L" + str(self.number)
      self.number += 1
      self.tree.append("{} [label=\"{}\",shape=box]".format(label, string))
      last = self._get_parent()
      if not last == -1:
        self.tree.append("{} -> {}".format(last, label))
      self.stack.append((label, self.current_depth))
  def _add_to_scope(self, name, value):
    return self.table.get_current_scope().insert(name, value)
  def _get_declaration(self, name):
    return self.table.get_current_scope().find(name)
  def _Program(self):
    if not self._token_type() == "PROGRAM":
      raise Parse_exception("PROGRAM is not declared")
    self._add_non_terminal("Program")
    self.current_depth += 1
    self._add_token()
    if not self._Identifier():
      raise Parse_exception("The Program is not named")
    program_name = self._get_last_token().data
    if not self._token_type() == ";":
      raise Parse_exception("The Program declaration is not terminated with a ';'")
    self._add_token()
    if self.create_symbol_table:
      self.table.push_scope()
    self.definitions = True
    self._Declarations()
    self.definitions = False
    if self.create_symbol_table and self.forward_declarations:
      for call in self.forward_declarations:
        name = call.procedure
        procedure_entry = self._get_declaration(name)
        if not procedure_entry:
          raise symbol_table.Symbol_table_exception("The procedure {} at ({}, {}) is undefined".format(call.procedure, call.start_position, call.end_position))
        call.procedure = procedure_entry
        start = call.start_position
        end = call.end_position
        if self.create_symbol_table and procedure_entry.formals:
          if not call.actuals:
            raise symbol_table.Symbol_table_exception("The call to function {} at ({}, {}) does not have the required number of arguments. Needed {}, given 0".format(name, start, end, len(procedure_entry.formals)))
          if not len(procedure_entry.formals) is len(call.actuals.expressions):
            raise symbol_table.Symbol_table_exception("The call to function {} at ({}, {}) does not have the required number of arguments. Needed {}, given {}".format(name, start, end, len(procedure_entry.formals), len(call.actuals.expressions)))
          for i, formal in enumerate(procedure_entry.formals):
            if not formal[1] is call.actuals.expressions[i].get_type():
              raise symbol_table.Symbol_table_exception("The type of argument {} is undefined for the call to {} at ({}, {})".format(i + 1, name, start, end))
      for check in self.type_checks:
        if not check[0].get_type() is check[1].get_type():
          raise ast.AST_exception("The types of the designator at ({}, {}) and the expression at ({}, {}) do not match".format(designator.start_position, designator.end_position, expression.start_position, expression.end_position))
      for check in self.integer_returns:
        if not type(check.get_type()) is symbol_table.Integer:
          raise symbol_table.Symbol_table_exception("The type returned by {} at ({}, {}) is not an integer".format(check.procedure.name, check.start_position, check.end_position))
    instructions = False
    if self._token_type() == "BEGIN":
      start, end = self._get_position()
      self._add_token()
      instructions = self._Instructions()
      if not instructions:
        raise Parse_exception("The BEGIN statement at ({}, {}) is not followed by instructions".format(start, end))
    if not self._token_type() == "END":
      start, end = self._get_position()
      raise Parse_exception("Syntax error at ({}, {}), expected an END".format(start, end))
    start, end = self._get_position()
    self._add_token()
    if self.create_symbol_table:
      self.table.leave_scope()
    if not self._Identifier():
      raise Parse_exception("There is no program specified to close after the END at ({}, {})".format(start, end))
    if not self._get_last_token().data == program_name:
      raise Parse_exception("The program {} following the END at ({}, {}) is unrecognized".format(self._get_last_token().data, start, end))
    if not self._token_type() == ".":
      raise Parse_exception("The program closed at ({}, {}) is not followed by a '.'".format(start, self._get_last_token().end_position))
    self._add_token()
    self.current_depth -= 1
    if self.create_ast:
      if not instructions:
        return False
      else:
        return ast.AST_tree(instructions)
  def _Declarations(self):
    self._add_non_terminal("Declarations")
    self.current_depth += 1
    while self._ConstDecl() or self._TypeDecl() or self._VarDecl() or self._ProcDecl():
      pass
    self.current_depth -= 1
    return True
  def _ConstDecl(self):
    if not self._token_type() == "CONST":
      return False
    self._add_non_terminal("ConstDecl")
    self.current_depth += 1
    self._add_token()
    start = self._token_position()
    while self._Identifier():
      if self.create_symbol_table:
        name = self._get_last_token().data
        id_start, id_end = self._get_position()
      if not self._token_type() == "=":
        raise Parse_exception("The constant at ({}, {}) is not followed by an '='".format(id_start, id_end))
      else:
        start_position, end_position = self._get_position()
        self._add_token()
        expression = self._Expression()
        if not expression:
          raise Parse_exception("The constant at ({}, {}) is not defined".format(id_start, id_end))
        if self.create_symbol_table:
          type_object = self._get_declaration("INTEGER")
          if not type(expression.child) is ast.Number:
            raise ast.AST_exception("The expression following the constant at ({}, {}) is not constant".format(id_start, id_end))
          value = expression.child.table_entry.value
          constant = symbol_table.Constant(start_position, end_position, type_object, value)
          if not self._add_to_scope(name, constant):
            old_start = self._get_declaration(name).start_position
            old_end = self._get_declaration(name).end_position
            raise symbol_table.Symbol_table_exception("The {} at ({}, {}) conflicts with the previous declaration at ({}, {})".format(name, id_start, id_end, old_start, old_end))  
        if not self._token_type() == ";":
          raise Parse_exception("The constant declaration at ({}, {}) is not followed by a ';'".format(id_start, id_end))
        else:
          self._add_token()
    self.current_depth -= 1
    return True
  def _TypeDecl(self):
    if not self._token_type() == "TYPE":
      return False
    self._add_non_terminal("TypeDecl")
    self.current_depth += 1
    self._add_token()
    while self._Identifier():
      if self.create_symbol_table:
        token = self._get_last_token()
        id_start, id_end = self._get_position()
      if not self._token_type() == "=":
        raise Parse_exception("The type definition at ({}, {}) is not followed by an '='".format(id_start, id_end))
      else:
        self._add_token()
        type_start = self._get_token().start_position
        base_type = self._Type()
        type_end = self._get_last_token().end_position
        if not base_type:
          raise Parse_exception("The type at ({}, {}) is not defined".format(type_start, type_end))
        if self.create_symbol_table:
          if not self._add_to_scope(token.data, base_type):
            old_start = self._get_declaration(token.data).start_position
            old_end = self._get_declaration(token.data).end_position
            raise symbol_table.Symbol_table_exception("The {} at ({}, {}) conflicts with the previous declaration at ({}, {})".format(token.data, id_start, id_end, old_start, old_end))  
        if not self._token_type() == ";":
          raise Parse_excpetion("The type declaration at ({}, {}) is not followed by a ';'".format(id_start, type_end))
        else:
          self._add_token()
    self.current_depth -= 1
    return True
  def _VarDecl(self):
    if not self._token_type() == "VAR":
      return False
    self._add_non_terminal("VarDecl")
    self.current_depth += 1
    self._add_token()
    start = self._token_position()
    identifiers = self._IdentifierList()
    while identifiers:
      end = self._get_last_token().end_position
      if not self._token_type() == ":":
        raise Parse_exception("The variable definition at ({}, {}) is not followed by an ':'".format(start, end))
      else:
        self._add_token()
        type_start = self._get_token().start_position
        type_object = self._Type()
        type_end = self._get_last_token().end_position
        if not type_object:
          raise Parse_exception("The variable type at ({}, {}) is not defined".format(type_start, type_end))
        if self.create_symbol_table:
          for identifier in identifiers:
            variable = symbol_table.Variable(identifier.start_position, identifier.end_position, type_object)
            if not self._add_to_scope(identifier.data, variable):
              old_start = self._get_declaration(identifier.data).start_position
              old_end = self._get_declaration(identifier.data).end_position
              raise symbol_table.Symbol_table_exception("The {} at ({}, {}) conflicts with the previous declaration at ({}, {})".format(identifier.data, identifier.start_position, identifier.end_position, old_start, old_end)) 
        if not self._token_type() == ";":
          raise Parse_excpetion("The variable declaration at ({}, {}) is not followed by a ';'".format(start, end))
        self._add_token()
      identifiers = self._IdentifierList()
    self.current_depth -= 1
    return True 
  def _Type(self):
    self._add_non_terminal("Type")
    self.current_depth += 1
    if self._Identifier():
      self.current_depth -= 1
      if self.create_symbol_table:
        identifier = self._get_last_token()
        type_object = self._get_declaration(identifier.data)
        if not type_object:
          raise symbol_table.Symbol_table_exception("The type {} at ({}, {}) has not been declared".format(identifier.data, identifier.start_position, identifier.end_position))
        elif not type(type_object) is symbol_table.Record and not type(type_object) is symbol_table.Array and not type(type_object) is symbol_table.Integer:
          raise symbol_table.Symbol_table_exception("The identifier {} at ({}, {}) is not a type".format(identifier.data, identifier.start_position, identifier.end_position))
        return type_object
      else:
        return True
    elif self._token_type() == "ARRAY":
      start, end = self._get_position()
      self._add_token()
      if self.create_symbol_table:
        token = self._get_last_token()
      expression = self._Expression()
      if not expression:
        raise Parse_exception("The ARRAY started at ({}, {}) is not followed by an expression".format(start, end))
      if self.create_symbol_table and (not type(expression.child) is ast.Number or not expression.child.table_entry.value > 0):
        raise ast.AST_exception("The length of the ARRAY at ({}, {}) is not an integer greater than zero".format(start, end))
      if self.create_symbol_table:
        length = expression.child.table_entry.value
      if not self._token_type() == "OF":
        raise Parse_exception("The ARRAY started at ({}, {}) is not followed by an 'OF'".format(start, end))
      else:
        self._add_token()
      element_type = self._Type()
      if not element_type:
        raise Parse_exception("The ARRAY started at ({}, {}) has no declared type".format(start, end))
      self.current_depth -= 1
      if self.create_symbol_table:
        return symbol_table.Array(token.start_position, token.end_position, element_type, length) 
      else:
        return True
    elif self._token_type() == "RECORD":
      start, end = self._get_position()
      self._add_token()
      if self.create_symbol_table:
        token = self._get_last_token()
        self.table.push_scope()
      identifiers = self._IdentifierList()
      while identifiers:
        if not self._token_type() == ":":
          raise Parse_exception("The RECORD started at ({}, {}), does not have a ':' following the IdentifierList.".format(start, end))
        else:
          self._add_token()
          type_object = self._Type()
          if not type_object:
            raise Parse_exception("The RECORD started at ({}, {}) has no type following the :".format(start, end))
          if self.create_symbol_table:
            for identifier in identifiers:
              variable = symbol_table.Variable(identifier.start_position, identifier.end_position, type_object)
              if not self._add_to_scope(identifier.data, variable):
                old_start = self._get_declaration(identifier.data).start_position
                old_end = self._get_declaration(identifier.data).end_position
                raise symbol_table.Symbol_table_exception("The {} at ({}, {}) conflicts with the previous declaration at ({}, {})".format(identifier.data, identifier.start_position, identifier.end_position, old_start, old_end))
          if not self._token_type() == ";":
            raise Parse_exception("The RECORD started at ({}, {}) has declarations that are not terminated with a ';'".format(start, end))
          else:
            self._add_token()
        identifiers = self._IdentifierList()
      if not self._token_type() == "END":
        raise Parse_exception("The RECORD started at ({}, {}) is not terminated by an END".format(start, end))
      self._add_token()
      self.current_depth -= 1
      if self.create_symbol_table:
        scope = self.table.get_current_scope()
        self.table.scopes.remove(scope)
        self.table.leave_scope()
        return symbol_table.Record(token.start_position, token.end_position, scope)
      else:
        return True
    else:
      return False
  def _Expression(self):
    self._add_non_terminal("Expression")
    self.current_depth += 1
    arithmetic = False
    negation = False
    if self._token_type() == "+" or self._token_type() == "-":
      arithmetic = True
      start = self._get_token().start_position
      end = self._get_token().end_position
      if self._token_type() == "-":
        negation = True
      self._add_token()
      term = self._Term()
      if not term:
        raise Parse_exception("The {} at ({}, {}) is not followed by a term".format(self._last_token_type(), start, end))
      if self.create_symbol_table:
        if type(term.child) is ast.Number:
          constant = symbol_table.Constant(start, start, self.table.get_int(), -term.child.table_entry.value)
          number = ast.Number(start, term.end_position, constant)
          term = ast.Expression(start, term.end_position, number)
        else:
          constant = symbol_table.Constant(start, start, self.table.get_int(), 0)
          number = ast.Number(start, start, constant)
          expression = ast.Expression(start, start, number)
          operator = scanner.Token("-", start, start, "-")
          binary = ast.Binary(start, term.end_position, operator, expression, term)
          term = ast.Expression(start, term.end_position, binary)
    else:
      term = self._Term()
      if not term:
        self._remove_from_tree()
        self.current_depth -= 1
        return False
    terms = [term]
    while self._token_type() == "+" or self._token_type() == "-":
      new_start = self._get_token().start_position
      new_end = self._get_token().end_position
      terms.append(self._get_token())
      self._add_token()
      term = self._Term()
      if not term:
        raise Parse_exception("Expected a term after the {} at ({}, {})".format(self._last_token_type(), new_start, new_end))
      terms.append(term)
    self.current_depth -= 1
    if self.create_symbol_table:
      if len(terms) is 1:
        last_node = terms[0]
        if arithmetic and self.definitions and type(last_node.child) is ast.Call and not type(last_node.child.procedure) is symbol_table.Procedure:
          self.integer_returns.append(last_node.child)
        elif arithmetic and type(last_node.get_type()) is not symbol_table.Constant and type(last_node.get_type()) is not symbol_table.Integer:
          raise ast.AST_exception("The term at ({}, {}) is not an integer".format(last_node.start_position, last_node.end_position))
      else:
        enum_terms = list(enumerate(terms))
        last_node = False
        for i, term in enum_terms[::2]:
          if self.definitions and type(term.child) is ast.Call and not type(term.child.procedure) is symbol_table.Procedure:
            self.integer_returns.append(term.child)
          elif type(term.get_type()) is not symbol_table.Constant and type(term.get_type()) is not symbol_table.Integer:
            raise ast.AST_exception("The term at ({}, {}) is not an integer".format(term.start_position, term.end_position))
          if not last_node:
            last_node = term
          else:
            if type(last_node.child) is ast.Number and type(term.child) is ast.Number:
              if terms[i - 1].data == "+":
                value = term.child.table_entry.value + last_node.child.table_entry.value
              else:
                value = last_node.child.table_entry.value - term.child.table_entry.value
              constant = symbol_table.Constant(last_node.start_position, term.end_position, self.table.get_int(), value)
              last_node = ast.Number(last_node.start_position, term.end_position, constant)
            else:
              last_node = ast.Binary(last_node.start_position, term.end_position, terms[i - 1], last_node, term)
            last_node = ast.Expression(last_node.start_position, last_node.end_position, last_node)
      return last_node
    else:
      return True
  def _Term(self):
    self._add_non_terminal("Term")
    self.current_depth += 1
    factor = self._Factor()
    if factor:
      factors = [factor]
      while self._token_type() == "*" or self._token_type() == "DIV" or self._token_type() == "MOD":
        factors.append(self._get_token())
        start, end = self._get_position()
        self._add_token()
        factor = self._Factor()
        if not factor:
          raise Parse_exception("Expected a factor after the {} at ({}, {})".format(self._last_token_type(), start, end))
        factors.append(factor)
      if self.create_symbol_table and len(factors) is 1:
        last_node = factors[0]
      elif self.create_symbol_table:
        enum_terms = list(enumerate(factors))
        last_node = False
        for i, factor in enum_terms[::2]:
          if self.definitions and type(factor.child) is ast.Call and not type(factor.child.procedure) is symbol_table.Procedure:
            self.integer_returns.append(factor.child)
          elif type(factor.get_type()) is not symbol_table.Constant and type(factor.get_type()) is not symbol_table.Integer:
            raise ast.AST_exception("The factor at ({}, {}) is not an integer".format(factor.start_position, factor.end_position))
          if not last_node:
            last_node = factor
          else:
            if type(factor.child) is ast.Number and factors[i - 1].data == "DIV":
              if factor.child.table_entry.value is 0:
                raise AST_exception("The right side of the DIV expression at ({}, {}) evaluated to 0".format(last_node.start_position, factor.end_position))
            if type(factor.child) is ast.Number and factors[i - 1].data == "MOD":
              if factor.child.table_entry.value is 0:
                raise AST_exception("The right side of the MOD expression at ({}, {}) evaluated to 0".format(last_node.start_position, factor.end_position))
            if type(last_node.child) is ast.Number and type(factor.child) is ast.Number:
              if factors[i - 1].data == "*":
                value = last_node.child.table_entry.value * factor.child.table_entry.value
              elif factors[i - 1].data == "DIV":
                value = last_node.child.table_entry.value / factor.child.table_entry.value
              else: # MOD
                value = factor.child.table_entry.value % last_node.child.table_entry.value
              constant = symbol_table.Constant(last_node.start_position, factor.end_position, self.table.get_int(), value)
              number = ast.Number(last_node.start_position, factor.end_position, constant)
              last_node = ast.Expression(number.start_position, number.end_position, number)
            elif type(last_node.child) is ast.Number and last_node.child.table_entry.value is 1 and factors[i - 1].data == "*":
              last_node = factor
            elif type(last_node.child) is ast.Number and last_node.child.table_entry.value is 0:
              constant = symbol_table.Constant(last_node.start_position, factor.end_position, self.table.get_int(), 0)
              number = ast.Number(last_node.start_position, factor.end_position, constant)
              last_node = ast.Expression(number.start_position, number.end_position, number)
            elif type(factor.child) is ast.Number and factor.child.table_entry.value is 0:
              constant = symbol_table.Constant(last_node.start_position, factor.end_position, self.table.get_int(), 0)
              number = ast.Number(last_node.start_position, factor.end_position, constant)
              last_node = ast.Expression(number.start_position, number.end_position, number)
            elif type(factor.child) is ast.Number and factor.child.table_entry.value is 1:
              continue
            else:
              binary = ast.Binary(last_node.start_position, factor.end_position, factors[i - 1], last_node, factor)
              last_node = ast.Expression(binary.start_position, binary.end_position, binary)
      self.current_depth -= 1
      if self.create_symbol_table:
        return last_node
      else:
        return True
    else:
      self.current_depth -= 1
      self._remove_from_tree()
      return False
  def _Factor(self):
    self._add_non_terminal("Factor")
    self.current_depth += 1
    integer = self._Integer()
    if integer:
      self.current_depth -= 1
      if self.create_symbol_table:
        expression = ast.Expression(integer.start_position, integer.end_position, integer)
        return expression
      else:
        return True
    designator = self._Designator()
    if designator:
      self.current_depth -= 1
      if self.create_symbol_table:
        expression = ast.Expression(designator.start_position, designator.end_position, designator)
        return expression
      else:
        return True
    if self._token_type() == "(":
      start, end = self._get_position()
      self._add_token()
      expression = self._Expression()
      if not expression:
        raise Parse_exception("The '(' at ({}, {}) does not contain an expression".format(start, end))
      elif not self._token_type() == ")":
        raise Parse_exception("The '(' at ({}, {}) is not closed".format(start, end))
      self._add_token()
      self.current_depth -= 1
      if self.create_symbol_table:
        return expression
      else:
        return True
    call = self._Call()
    if call:
      self.current_depth -= 1
      if self.create_symbol_table:
        expression = ast.Expression(call.start_position, call.end_position, call)
        return expression
      else:
        return True
    self._remove_from_tree()
    self.current_depth -= 1
    return False
  def _Instructions(self):
    self._add_non_terminal("Instructions")
    self.current_depth += 1
    instruction = self._Instruction()
    if not instruction:
      self.current_depth -= 1
      return False
    if self.create_ast:
      instructions = [instruction]
    while self._token_type() == ";":
      self._add_token()
      instruction = self._Instruction()
      if not instruction:
        break
      if self.create_ast:
        instructions.append(instruction)
    self.current_depth -= 1
    if self.create_ast:
      return ast.Instructions(instructions[0].start_position, instructions[len(instructions) - 1].end_position, instructions)
    else:
      return True
  def _Instruction(self):
    self._add_non_terminal("Instruction")
    self.current_depth += 1
    If = self._If()
    if If:
      self.current_depth -= 1
      if self.create_ast:
        return If
      else:
        return True
    repeat = self._Repeat()
    if repeat:
      self.current_depth -= 1
      if self.create_ast:
        return repeat
      else:
        return True
    While = self._While()
    if While:
      self.current_depth -= 1
      if self.create_ast:
        return While
      else:
        return True
    read = self._Read()
    if read:
      self.current_depth -= 1
      if self.create_ast:
        return read
      else:
        return True
    write = self._Write()
    if write:
      self.current_depth -= 1
      if self.create_ast:
        return write
      else:
        return True
    assign = self._Assign()
    if assign:
      self.current_depth -= 1
      if self.create_ast:
        return assign 
      else:
        return True
    call = self._Call()
    if call:
      self.current_depth -= 1
      if self.create_ast:
        return call
      else:
        return True
    self.current_depth -= 1
    self._remove_from_tree()
    return False
  def _Assign(self):
    self._add_non_terminal("Assign")
    self.current_depth += 1
    start = self._get_token().start_position
    designator = self._Designator()
    if not designator:
      self.current_depth -= 1
      self._remove_from_tree()
      return False
    if self.create_ast and type(designator) is ast.Number:
      raise ast.AST_exception("The designator at ({}, {}) does not represent a variable".format(designator.start_position, designator.end_position))
    end = self._get_last_token().end_position
    if not self._token_type() == ":=":
      raise Parse_exception("There is no assignment operator after the designator at ({}, {})".format(start, end))
    start, end = self._get_position()
    self._add_token()
    expression = self._Expression()
    if not expression:
      raise Parse_exception("The assignment := at ({}, {}) is not defined".format(start, end))
    self.current_depth -= 1
    if self.create_ast:
      if self.definitions and type(expression.child) is ast.Call and not type(expression.child.procedure) is symbol_table.Procedure:
        self.type_checks.append((designator, expression))
      elif not designator.get_type() is expression.get_type():
        raise ast.AST_exception("The types of the designator at ({}, {}) and the expression at ({}, {}) do not match".format(designator.start_position, designator.end_position, expression.start_position, expression.end_position))
      return ast.Assign(designator.start_position, expression.end_position, designator, expression)
    else:
      return True
  def _If(self):
    if not self._token_type() == "IF":
      return False
    self._add_non_terminal("If")
    self.current_depth += 1
    start, end = self._get_position()
    self._add_token()
    condition = self._Condition()
    if not condition:
      raise Parse_exception("The IF statement at ({}, {}) is not followed by a condition".format(start, end))
    if not self._token_type() == "THEN":
      raise Parse_exception("The IF statement at ({}, {}) is not followed by a THEN".format(start, end))
    then_start, then_end = self._get_position()
    self._add_token()
    instructions_true = self._Instructions()
    if not instructions_true:
      raise Parse_exception("The THEN statement at ({}, {}) is not followed by any instructions".format(then_start, then_end))
    instructions_false = False
    if self._token_type() == "ELSE":
      else_start, else_end = self._get_position()
      self._add_token()
      instructions_false = self._Instructions()
      if not instructions_false:
        raise Parse_exception("The ELSE at ({}, {}) is not followed by any instructions".format(else_start, else_end))
    if not self._token_type() == "END":
      raise Parse_exception("The IF at ({}, {}) is not followed by an END".format(start, end))
    end = self._get_token().end_position
    self._add_token()
    self.current_depth -= 1
    if self.create_ast:
      return ast.If(start, end, condition, instructions_true, instructions_false)
    else:
      return True
  def _Repeat(self):
    if not self._token_type() == "REPEAT":
      return False
    self._add_non_terminal("Repeat")
    self.current_depth += 1
    start, end = self._get_position()
    self._add_token()
    instructions = self._Instructions()
    if not instructions:
      raise Parse_exception("The REPEAT at ({}, {}) is not followed by any instructions".format(start, end))
    if not self._token_type() == "UNTIL":
      raise Parse_exception("The REPEAT at ({}, {}) is not followed by an UNTIL".format(start, end))
    until_start, until_end = self._get_position()
    self._add_token()
    condition = self._Condition()
    if not condition:
      raise Parse_exception("The UNTIL at ({}, {}) is not followed by a condition".format(until_start, until_end))
    if not self._token_type() == "END":
      raise Parse_exception("The REPEAT at ({}, {}) is not terminated by an END".format(start, end))
    end = self._get_token().end_position
    self._add_token()
    self.current_depth -= 1
    if self.create_ast:
      return ast.Repeat(start, end, condition, instructions)
    else:
      return True
  def _While(self):
    if not self._token_type() == "WHILE":
      return False
    self._add_non_terminal("While")
    self.current_depth += 1
    start, end = self._get_position()
    self._add_token()
    condition = self._Condition()
    if not condition:
      raise Parse_exception("The WHILE at ({}, {}) is not followed by a condition".format(start, end))
    if not self._token_type() == "DO":
      raise Parse_exception("The WHILE at ({}, {}) is not followed by a DO".format(start, end))
    do_start, do_end = self._get_position()
    self._add_token()
    instructions = self._Instructions()
    if not instructions:
      raise Parse_exception("The DO at ({}, {}) is not followed by any instructions".format(do_start, do_end))
    if not self._token_type() == "END":
      raise Parse_exception("The WHILE at ({}, {}) is not followed by an END".format(start, end))
    end = self._get_token().end_position
    self._add_token()
    self.current_depth -= 1
    if self.create_ast:
      relation = condition.relation.data
      if relation == "=":
        negated_relation = scanner.Token("#", start, start, "#")
      elif relation == "#":
        negated_relation = scanner.Token("=", start, start, "=")
      elif relation == "<":
        negated_relation = scanner.Token(">=", start, start, ">=")
      elif relation == ">":
        negated_relation = scanner.Token("<=", start, start, "<=")
      elif relation == "<=":
        negated_relation = scanner.Token(">", start, start, ">")
      else:
        negated_relation = scanner.Token("<", start, start, "<")
      negated_condition = ast.Condition(start, start, negated_relation, condition.expression_left, condition.expression_right)
      repeat = ast.Repeat(start, end, negated_condition, instructions)
      instructions = ast.Instructions(start, end, [repeat])
      return ast.If(start, end, condition, instructions, False)
    else:
      return True
  def _Condition(self):
    self._add_non_terminal("Condition")
    self.current_depth += 1
    start, end = self._get_position()
    expression_left = self._Expression()
    if not expression_left:
      self._remove_from_tree()
      self.current_depth -= 1
      return False
    if not (self._token_type() == "=" or self._token_type() == "#" or self._token_type() == "<"):
      if not (self._token_type() == ">" or self._token_type() == "<=" or self._token_type() == ">="):
        raise Parse_exception("The condition at ({}, {}) has no operator".format(start, end))
    relation = self._get_token()
    self._add_token()
    expression_right = self._Expression()
    if not expression_right:
      raise Parse_exception("The condition at ({}, {}) has no second expression".format(start, end))
    self.current_depth -= 1
    if self.create_ast:
      if not type(expression_left.get_type()) is symbol_table.Constant and not type(expression_left.get_type()) is symbol_table.Integer:
        raise ast.AST_exception("The expression at ({}, {}) is not an integer".format(expression_left.start_position, expression_left.end_position))
      if not type(expression_right.get_type()) is symbol_table.Constant and not type(expression_right.get_type()) is symbol_table.Integer:
        raise ast.AST_exception("The expression at ({}, {}) is not an integer".format(expression_right.start_position, expression_right.end_position))
      return ast.Condition(expression_left.start_position, expression_right.end_position, relation, expression_left, expression_right)
    else:
      return True
  def _Write(self):
    if not self._token_type() == "WRITE":
      return False
    start, end = self._get_position()
    self._add_non_terminal("Write")
    self.current_depth += 1
    self._add_token()
    expression = self._Expression()
    if not expression:
      raise Parse_exception("The WRITE at ({}, {}) has no specified expression to write".format(start, end))
    self.current_depth -= 1
    if self.create_ast:
      if not type(expression.get_type()) is symbol_table.Constant and not type(expression.get_type()) is symbol_table.Integer:
        raise ast.AST_exception("The expression at ({}, {}) is not an integer".format(expression.start_position, expression.end_position))
      return ast.Write(start, expression.end_position, expression)
    else: 
      return True
  def _Read(self):
    if not self._token_type() == "READ":
      return False
    read_start = self._get_token().start_position
    read_end = self._get_token().end_position
    self._add_non_terminal("Read")
    self.current_depth += 1
    self._add_token()
    location = self._Designator()
    if not location:
      raise Parse_exception("The READ at ({}, {}) has no specified location to read from".format(read_start, read_end))
    self.current_depth -= 1
    if self.create_ast:
      if not type(location) is ast.Variable and not type(location.get_type()) is symbol_table.Integer:
        raise ast.AST_exception("The location at ({}, {}) following the READ at ({}, {}) is not a variable of type INTEGER".format(location.start_position, location.end_position, read_start, read_end))
      return ast.Read(read_start, location.end_position, location)
    else: 
      return True
  def _Designator(self):
    self._add_non_terminal("Designator")
    self.current_depth += 1
    if self.create_symbol_table:
      name = self._get_token().data
      table_entry = self._get_declaration(name)
      if not table_entry or type(table_entry) is symbol_table.Procedure:
        self._remove_from_tree()
        self.current_depth -= 1
        return False
    if not self._Identifier():
      self._remove_from_tree()
      self.current_depth -= 1
      return False
    if self._token_type() == "(":
        self._remove_from_tree()
        self._remove_from_tree()
        self.position -= 1
        self.current_depth -= 1
        return False
    if self.create_symbol_table:
      start_position, end_position = self._get_last_position()
      if type(table_entry) is symbol_table.Record or type(table_entry) is symbol_table.Array or type(table_entry) is symbol_table.Integer:
        raise ast.AST_exception("{} at ({}, {}) is a type".format(name, start_position, end_position))
      if type(table_entry) is symbol_table.Constant:
        node = ast.Number(start_position, end_position, table_entry)
        if self._Selector():
          raise ast.AST_exception("{} at ({}, {}) is a constant and cannot be followed by a selector".format(name, start_position, end_position))
        self.current_depth -= 1
        return ast.Number(start_position, end_position, table_entry)
      elif type(table_entry.type_object) is symbol_table.Record:
        last_type = True
      else:
        last_type = False
      variable = ast.Variable(start_position, end_position, name, table_entry)
      last_node = ast.Location(start_position, end_position, variable)
    selectors = self._Selector()
    if self.create_symbol_table and selectors:
      for selector in selectors:
        if selector[0]:
          if type(last_node.child) is ast.Variable:
            if not type(last_node.child.table_entry.type_object) is symbol_table.Record:
              raise ast.AST_exception("The designator at ({}, {}) is not a record; it has no field {} at ({}, {})".format(last_node.start_position, last_node.end_position, selector[1], selector[2], selector[3]))
            table_entry = last_node.child.table_entry.type_object.scope_object.find(selector[1])
          elif not last_type:
            if not type(last_node.child.location.get_type().element_type) is symbol_table.Record:
              raise ast.AST_exception("The designator at ({}, {}) is not a record; it has no field {} at ({}, {})".format(last_node.start_position, last_node.end_position, selector[1], selector[2], selector[3]))
            table_entry = last_node.child.location.get_type().element_type.scope_object.find(selector[1])
          else:
            table_entry = last_node.child.variable.table_entry.type_object.scope_object.find(selector[1])
          if not table_entry:
            if last_type:
              raise ast.AST_exception("The field {} at ({},{}) is not defined in the record {}".format(selector[1], selector[2], selector[3], last_node.child.name))
            else:
              raise ast.AST_exception("The field {} at ({}, {}) is not defined in the array {}".format(selector[1], selector[2], selector[3], last_node.child.location.child.name))
          variable = ast.Variable(selector[2], selector[3], selector[1], table_entry)
          last_node = ast.Field(last_node.start_position, selector[3], last_node, variable)
          last_type = True
        else:
          if not type(last_node.get_type()) is symbol_table.Array:
            raise ast.AST_exception("the index at ({}, {}) modifies a non-array object".format(selector[2], selector[3]))
          if type(last_node.child) is ast.Variable:
            last_node = ast.Index(last_node.start_position, selector[3], last_node, selector[1], last_node.child.table_entry.type_object)
          elif last_type:
            last_node = ast.Index(last_node.start_position, selector[3], last_node, selector[1], last_node.child.variable.table_entry.type_object)
          else:
            last_node = ast.Index(last_node.start_position, selector[3], last_node, selector[1], last_node.child.table_entry.element_type)
          if type(selector[1].child) is ast.Number:
            if not 0 <= selector[1].child.table_entry.value < last_node.table_entry.length:
              raise symbol_table.Symbol_table_exception("Index {} at ({}, {}) out range for array of length {}".format(selector[1].child.table_entry.value, last_node.start_position, last_node.end_position, last_node.table_entry.length))
          last_type = False
        last_node = ast.Location(last_node.start_position, last_node.end_position, last_node)
    self.current_depth -= 1
    if self.create_symbol_table:
      return last_node
    else:
      return True
  def _Selector(self):
    self._add_non_terminal("Selector")
    self.current_depth += 1
    if self.create_symbol_table:
      selectors = []
    while self._token_type() == "[" or self._token_type() == ".":
      if self._token_type() == "[":
        start, end = self._get_position()
        self._add_token()
        expression_list = self._ExpressionList()
        if not expression_list:
          raise Parse_exception("There is no ExpressionList in the '[' started at ({}, {})".format(start, end))
        if not self._token_type() == "]":
          raise Parse_exception("The '[' started at ({}, {}) is not closed".format(start, end))
        self._add_token()
        if self.create_symbol_table:
          selectors[len(selectors):] = expression_list
      elif self._token_type() == ".":
        start, end = self._get_position()
        self._add_token()
        if not self._Identifier():
          raise Parse_exception("The '.' at ({}, {}) is not followed by an identifier".format(start, end))
        if self.create_symbol_table:
          selectors.append((True, self._get_last_token().data, self._get_last_token().start_position, self._get_last_token().end_position))
    self.current_depth -= 1
    if self.create_symbol_table:
      return selectors
    else:
      return True
  def _IdentifierList(self):
    self._add_non_terminal("IdentifierList")
    self.current_depth += 1
    start, end = self._get_position()
    if not self._Identifier():
      self._remove_from_tree()
      self.current_depth -= 1
      return False
    identifiers = [self._get_last_token()]
    while self._token_type() == ",":
      new_start, new_end = self._get_position()
      self._add_token()
      if not self._Identifier():
        raise Parse_exception("In the IdentifierList started at ({}, {}): The ',' at ({}, {}) is not followed by an identifier".format(start, end, new_start, new_end))
      identifiers.append(self._get_last_token())
    self.current_depth -= 1
    return identifiers
  def _ExpressionList(self):
    self._add_non_terminal("ExpressionList")
    self.current_depth += 1
    start = self._get_token().start_position
    end = self._get_token().end_position
    indices = []
    expression = self._Expression()
    if expression:
      if self.create_symbol_table:
        indices.append((False, expression, expression.start_position - 1, expression.end_position + 1))
      while self._token_type() == ",":
        new_start = self._get_token().start_position
        new_end = self._get_token().end_position
        self._add_token()
        expression = self._Expression()
        if not expression:
          raise Parse_exception("In the ExpressionList started at ({}, {}): The ',' at ({}, {}) is not followed by an expression".format(start, end, new_start, new_end))
        if self.create_symbol_table:
          indices.append((False, expression, expression.start_position - 1, expression.end_position + 1))
      self.current_depth -= 1
      if self.create_symbol_table:
        return indices
      else:
        return True
    else:
      self._remove_from_tree()
      self.current_depth -= 1
      return False
  def _Identifier(self):
    if not self._token_type() == "identifier":
      return False
    data = self._get_token().data
    self._add_token()
    return data
  def _Integer(self):
    if not self._token_type() == "integer":
      return False
    self._add_token()
    if self.create_symbol_table:
      value = self._get_last_token().data
      start = self._get_last_token().start_position
      end = self._get_last_token().end_position
      constant = symbol_table.Constant(start, end, self.table.get_int(), value)
      return ast.Number(start, end, constant)
    else:
      return True
  def _ProcDecl(self):
    if not self._token_type() == "PROCEDURE":
      return False
    self._add_non_terminal("ProcDecl")
    self.current_depth += 1
    proc_start, proc_end = self._get_position()
    self._add_token()
    name = self._get_token().data
    name_start, name_end = self._get_position()
    if not self._Identifier():
      raise Parse_exception("The PROCEDURE at ({}, {}) is not named".format(proc_start, proc_end))
    if not self._token_type() == "(":
      raise Parse_exception("The PROCEDURE {} at ({}, {}) is not folled by a '('".format(proc_start, proc_end))
    start = self._get_position()[0]
    self._add_token()
    if self.create_symbol_table:
      self.table.push_scope()
    formals = self._Formals()
    if self.create_symbol_table and formals:
      for formal in formals:
        variable = symbol_table.Variable(formal[0].start_position, formal[0].end_position, formal[1])
        if not self._add_to_scope(formal[0].data, variable):
          previous = self._get_declaration(formal[0].data)
          raise Parse_exception("The variable {} at ({}, {}) was already declared at ({}, {})".format(formal[0].data, formal[0].start_position, formal[0].end_position, previous.start_position, previous.end_position))
    if not self._token_type() == ")":
      raise Parse_exception("The '(' at ({}, {}) is not closed".format(start, start))
    self._add_token()
    return_type = False
    if self._token_type() == ":":
      start = self._get_position()[0]
      self._add_token()
      return_type = self._Type()
      if not return_type:
        raise Parse_exception("The ':' at ({}, {}) is not followed by a return type".format(start, start))
    if not self._token_type() == ";":
      raise Parse_exception("The PROCEDURE name declaration at ({}, {}) is not followed by a ';'".format(proc_start, name_end))
    self._add_token()
    self._VarDecl()
    instructions = False
    if self._token_type() == "BEGIN":
      self._add_token()
      instructions = self._Instructions()
    return_expression = False
    if self._token_type() == "RETURN":
      start, end = self._get_position()
      self._add_token()
      return_expression = self._Expression()
      if not return_expression:
        raise Parse_exception("The RETURN at ({}, {}) is not followed by an expression".format(start, end))
      if self.create_symbol_table:
        if not return_expression.get_type() == return_type:
          raise symbol_table.Symbol_table_exception("The declared return type does not match the return expression at ({}, {})".format(return_expression.start_position, return_expression.end_position))
    if self.create_symbol_table:
      scope = self.table.get_current_scope()
      self.table.scopes.remove(scope)
      self.table.leave_scope()
    if not self._token_type() == "END":
      raise Parse_exception("The PROCEDURE declaration at ({}, {}) is not followed by an END".format(proc_start, proc_end))
    start, end = self._get_position()
    self._add_token()
    end_name = self._get_token().data
    name2_start, name2_end = self._get_position()
    if not self._Identifier():
      raise Parse_exception("The END at ({}, {}) is not followed by a procedure name".format(start, end))
    if not end_name == name:
      raise Parse_exception("The procedure {} at ({}, {}) does not match the label {} at at its closing at ({}, {})".format(name, name_start, name_end, end_name, name2_start, name2_end))
    if not self._token_type() == ";":
      raise Parse_exception("The PROCEDURE declaration at ({}, {}) is not followed by a ';'".format(proc_start, name2_end))
    end = self._get_position()[1]
    self._add_token()
    self.current_depth -= 1
    if self.create_symbol_table:
      procedure = symbol_table.Procedure(proc_start, end, name, formals, return_type, scope, instructions, return_expression)
      if not self._add_to_scope(name, procedure):
        previous = self._get_declaration(name)
        raise symbol_table.Symbol_table_exception("The declaration of {} at ({}, {}) conflicts with the previous declaration at ({}, {})".format(name, proc_start, end, previous.start_position, previous.end_position))
    return True
  def _Formals(self):
    self._add_non_terminal("Formals")
    self.current_depth += 1
    formal = self._Formal()
    if not formal:
      self._remove_from_tree()
      self.current_depth -= 1
      return False
    formals = []
    if self.create_symbol_table:
      for variable in formal[0]:
        formals.append((variable, formal[1]))
    while self._token_type() == ";":
      start = self._get_position()[0]
      self._add_token()
      formal = self._Formal()
      if not formal:
        raise Parse_exception("The ';' at ({}, {}) is not followed by a formal".format(start, start))
      for variable in formal[0]:
        formals.append((variable, formal[1]))
    self.current_depth -= 1
    if self.create_symbol_table:
      return formals
    else:
      return True
  def _Formal(self):
    self._add_non_terminal("Formal")
    self.current_depth += 1
    identifiers = self._IdentifierList()
    if not identifiers:
      self._remove_from_tree()
      self.current_depth -= 1
      return False
    start = identifiers[0].start_position
    end = identifiers[len(identifiers) - 1].end_position
    if not self._token_type() == ":":
      raise Parse_exception("The Formal declaration at ({}, {}) is not followed by a ':'".format(start, end))
    end = self._get_position()[1]
    self._add_token()
    type_object = self._Type()
    if not type_object:
      raise Parse_exception("The Formal declaration at ({}, {}) is not followed by a type".format(start, end))
    self.current_depth -= 1
    if self.create_symbol_table:
      return identifiers, type_object
    else:
      return True
  def _Call(self):
    self._add_non_terminal("Call")
    self.current_depth += 1
    call_start, call_end = self._get_position()
    procedure = self._Identifier()
    if not procedure:
      self._remove_from_tree()
      self.current_depth -= 1
      return False
    if self.create_symbol_table:
      procedure_entry = self._get_declaration(procedure)
      forward_declaration = False
      if not procedure_entry:
        if self.definitions:
          forward_declaration = True
        elif self._token_type() == "(":
          raise symbol_table.Symbol_table_exception("The process {} at ({}, {}) is undefined".format(procedure, call_start, call_end))
        else:
          raise symbol_table.Symbol_table_exception("The identifier {} at ({}, {}) is undefined".format(procedure, call_start, call_end))
    if not self._token_type() == "(":
      raise Parse_exception("The procedure call at ({}, {}) is not followed by a '('".format(call_start, call_end))
    start = self._get_position()[0]
    self._add_token()
    actuals = self._Actuals()
    if self.create_symbol_table and not forward_declaration and procedure_entry.formals:
      if not actuals:
        raise symbol_table.Symbol_table_exception("The call to function {} at ({}, {}) does not have the required number of arguments. Needed {}, given 0".format(procedure, call_start, start, len(procedure_entry.formals)))
      if not len(procedure_entry.formals) is len(actuals.expressions):
        raise symbol_table.Symbol_table_exception("The call to function {} at ({}, {}) does not have the required number of arguments. Needed {}, given {}".format(procedure, call_start, start, len(procedure_entry.formals), len(actuals.expressions)))
      for i, formal in enumerate(procedure_entry.formals):
        if not formal[1] is actuals.expressions[i].get_type():
          raise symbol_table.Symbol_table_exception("The type of argument {} is undefined for the call to {} at ({}, {})".format(i + 1, procedure, call_start, start))
    if not self._token_type() == ")":
      raise Parse_exception("The '(' at ({}, {}) is not closed by a ')'".format(start, start))
    call_end = self._get_position()[1]
    self._add_token()
    self.current_depth -= 1
    if self.create_symbol_table:
      if forward_declaration:
        call = ast.Call(call_start, call_end, procedure, actuals)
        self.forward_declarations.append(call)
      else:
        call = ast.Call(call_start, call_end, procedure_entry, actuals)
      return call
    else:
      return True
  def _Actuals(self):
    self._add_non_terminal("Actuals")
    self.current_depth += 1
    expressions = self._ExpressionList()
    self.current_depth -= 1
    if not expressions:
      self._remove_from_tree()
      return False
    elif self.create_symbol_table:
      start = expressions[0][1].start_position
      end = expressions[len(expressions) - 1][1].end_position
      old_expressions = expressions
      expressions = []
      for expression in old_expressions:
        expressions.append(expression[1])
      return ast.Actuals(start, end, expressions)
    else:
      return True
  def print_tree(self):
    if self.graphical:
      print "strict digraph CST {"
      for line in self.tree:
        print line
      print "}"
    else:
      for line in self.tree:
        if line[0] == True:
          print "  " * line[2] + line[1]
        else:
          print "  " * line[2] + line[1].__repr__()
  def parse(self):
    if self.create_ast:
      abstract_syntax_tree = self._Program()
    else:
      self._Program()
    if self.create_symbol_table and self.create_ast:
      return self.table, abstract_syntax_tree
    elif self.create_symbol_table:
      return self.table

