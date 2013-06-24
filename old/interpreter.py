import ast
import symbol_table
from environment import IntegerBox, Environment

class Interpreter_exception(Exception):
  def __init__(self, error):
    self.error = error
  def __str__(self):
    return "error: {}".format(self.error)

class Interpreter(object):
  def __init__(self, environment, tree):
    self.base_environment = environment
    self.environment = environment
    self.tree = tree
  def _create_environment(self, call):
    values = call.procedure.scope.create_environment()
    for name in self.base_environment.boxes:
      if not name in values:
        values[name] = self.base_environment.boxes[name]
    if call.actuals:
      for i, actual in enumerate(call.actuals.expressions):
        name = call.procedure.formals[i][0].data
        if type(actual.child.get_type()) is not symbol_table.Integer:
          values[name] = self._get_box(actual.child)
        else:
          argument = self._evaluate_expression(actual)
          formal = values[name]
          formal.value = argument
    new_environment = Environment()
    new_environment.boxes = values
    return new_environment
  def _evaluate_call(self, call):
    old_environment = self.environment
    self.environment = self._create_environment(call)
    if  call.procedure.instructions:
      for instruction in call.procedure.instructions.get_instructions():
        self._do_instruction(instruction)
    if call.procedure.return_expression:
      return_value = self._evaluate_expression(call.procedure.return_expression)
    self.environment = old_environment
    if call.procedure.return_expression:
      return return_value
  def _evaluate_expression(self, expression):
    if type(expression.child) is ast.Number:
      return expression.child.table_entry.value
    elif type(expression.child) is ast.Location:
      return self._get_box(expression.child).value
    elif type(expression.child) is ast.Binary:
      left_result = self._evaluate_expression(expression.child.expression_left)
      right_result = self._evaluate_expression(expression.child.expression_right)
      if expression.child.operator.data == "+":
        return left_result + right_result
      elif expression.child.operator.data == "-":
        return left_result - right_result
      elif expression.child.operator.data == "*":
        return left_result * right_result
      elif expression.child.operator.data == "DIV":
        if right_result is 0:
          raise Interpreter_exception("The right side of DIV expression at ({}, {}) evaluated to 0".format(expression.start_position, expression.end_position))
        return left_result / right_result
      else: # MOD
        if right_result is 0:
          raise Interpreter_exception("The right side of MOD expression at ({}, {}) evaluated to 0".format(expression.start_position, expression.end_position))
        return left_result % right_result
    elif type(expression.child) is ast.Call:
      return self._evaluate_call(expression.child)
  def _evaluate_condition(self, condition):
    left_result = self._evaluate_expression(condition.expression_left)
    right_result = self._evaluate_expression(condition.expression_right)
    if condition.relation.data == "=":
      return left_result is right_result
    elif condition.relation.data == "#":
      return not left_result is right_result
    elif condition.relation.data == "<":
      return left_result < right_result
    elif condition.relation.data == ">":
      return left_result > right_result
    elif condition.relation.data == "<=":
      return left_result <= right_result
    else: # >=
      return left_result >= right_result
  def _get_box(self, location):
    self.stack.append(False)
    self.__get_box(location.child)
    return self.stack.pop()
  def __get_box(self, location):
    if type(location) is ast.Field:
      self.__get_box(location.location.child)
      record = self.stack.pop()
      self.stack.append(record.get_box(location.variable.name))
    elif type(location) is ast.Index:
      self.__get_box(location.location.child)
      array = self.stack.pop()
      index = self._evaluate_expression(location.expression)
      box = array.get_box(index)
      if not box:
        raise Interpreter_exception("Index out of range; the expression at ({}, {}) evaluates to {}".format(location.expression.start_position, location.expression.end_position, index))
      self.stack.append(box)
    else: # Variable
      environment = self.stack.pop()
      if not environment:
        environment = self.environment
      self.stack.append(self.environment.get_box(location.name))
  def _do_assign(self, node):
    box = self._get_box(node.location)
    if type(box) is IntegerBox:
      result = self._evaluate_expression(node.expression)
      box.value = result
    else:
      box.set_to(self._get_box(node.expression.child))
  def _do_if(self, node):
    if self._evaluate_condition(node.condition):
      for instruction in node.instructions_true.get_instructions():
        self._do_instruction(instruction)
    elif node.instructions_false:
      for instruction in node.instructions_false.get_instructions():
        self._do_instruction(instruction)
  def _do_repeat(self, node):
    while 1:
      for instruction in node.instructions.get_instructions():
        self._do_instruction(instruction)
      if self._evaluate_condition(node.condition):
        break
  def _do_read(self, node):
    value = raw_input()
    try:
      value = int(value)
    except ValueError:
      raise Interpreter_exception("{} is not an integer".format(value))
    box = self._get_box(node.location)
    box.value = value
  def _do_write(self, node):
    print self._evaluate_expression(node.expression)
  def _do_instruction(self, instruction):
    if type(instruction) is ast.Assign:
      self._do_assign(instruction)
    elif type(instruction) is ast.If:
      self._do_if(instruction)
    elif type(instruction) is ast.Repeat:
      self._do_repeat(instruction)
    elif type(instruction) is ast.Read:
      self._do_read(instruction)
    elif type(instruction) is ast.Call:
      self._evaluate_call(instruction)
    else: # Write
      self._do_write(instruction)
  def run(self):
    if self.tree:
      self.stack = []
      for instruction in self.tree.get_instructions():
        self._do_instruction(instruction)

