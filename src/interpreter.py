import syntax_tree
import symbol_table
import environment

class Interpreter_error(Exception):
  def __init__(self, error):
    self.error = error
  def __str__(self):
    return "error: {}".format(error)

class Interpreter(object):
  def run(self, tree, table):
    self.environment = environment.Environment(table.scopes[1])
    self.tree = tree
    for instruction in self.tree.instructions.instructions:
      self.do_instruction(instruction)
  def do_instruction(self, instruction):
    if type(instruction) is syntax_tree.Assign:
      self.do_assign(instruction)
    elif type(instruction) is syntax_tree.If:
      self.do_if(instruction)
    elif type(instruction) is syntax_tree.Repeat:
      self.do_repeat(instruction)
    elif type(instruction) is syntax_tree.Read:
      self.do_read(instruction)
    elif type(instruction) is syntax_tree.Call:
      self.do_call(instruction)
    else: # Write
      self.do_write(instruction)
  def do_assign(self, assign):
    box = self.get_box(assign.location)
    box.set_to(self.evaluate_expression(assign.expression))
  def do_if(self, if_instruction):
    if self.evaluate_condition(if_instruction.condition):
      for instruction in if_instruction.instructions_true.instructions:
        self.do_instruction(instruction)
    elif if_instruction.instructions_false:
      for instruction in if_instruction.instructions_false.instructions:
        self.do_instruction(instruction)
  def do_repeat(self, repeat):
    while 1:
      for instruction in repeat.instructions.instructions:
        self.do_instructions(instruction)
      if self.evaluate_condition(repeat.condition):
        break
  def do_read(self, read):
    value = raw_input()
    try:
      value = int(value)
    except ValueError:
      raise Interpreter_error("{} is not an INTEGER".format(value))
    box = self.get_box(read.location)
    box.value = value
  def do_call(self, call):
    old_environment = self.environment
    self.environment = environment.Environment(call.definition.scope)
    if call.definition.instructions:
      for instruction in call.definition.instructions.instruction:
        self.do_instruction(instruction)
    if self.definition.return_expression:
      result = self.evaluate_expression(call.definition.return_expression)
      self.environment = old_environment
      return result
    self.environment = old_environment
  def do_write(self, write):
    print self.evaluate_expression(node.expression)
  def evaluate_expression(self, expression):
    if type(expression.child) is syntax_tree.Number:
      return expression.child.table_entry.value
    elif type(expression.child) is syntax_tree.Location:
      return self.get_box(expression.child)
    elif type(expression.child) is syntax_tree.Call:
      return self.do_call(expression.child)
    elif type(expression.child) is syntax_tree.Binary:
      left_result = self.evaluate_expression(expression.child.expression_left)
      right_result = self.evaluate_expression(expression.child.expression_right)
      if expression.child.operator == '+':
        return left_result + right_result
      elif expression.child.operator == '-':
        return left_result - right_result
      elif expression.child.operator == '*':
        return left_result * right_result
      elif expression.child.operator == 'DIV':
        if right_result is 0:
          raise Interpreter_error("The right side of the 'DIV' on line {} evaluated to 0".
                                    format(expression.child.expression_right.line))
        return left_result / right_result
      else: # MOD
        if right_result is 0:
          raise Interpreter_error("The right side of the 'DIV' on line {} evaluated to 0".
                                    format(expression.child.expression_right.line))
        return left_result % right_result
  def evaluate_condition(self, condition):
    left_result = self.evaluate_expression(condition.expression_left)
    right_result = self.evaluate_expression(condition.expression_right)
    if condition.relation == '=':
      return left_result is right_result
    elif condition.relation == '#':
      return not left_result is right_result
    elif condition.relation == '<':
      return left_result < right_result
    elif condition.relation == '>':
      return left_result > right_result
    elif condition.relation == '<=':
      return left_result <= right_result
    else: # >=
      return left_result >= right_result
  def get_box(self, location):
    if type(location.child) is syntax_tree.Field:
      record_box = self.get_box(location.child.location)
      return record_box.get_box(variable.name)
    elif type(location.child) is syntax_tree.Index:
      array_box = self.get_box(location.child.location)
      index = self.evaluate_expression(location.child.expression)
      box = array_box.get_box(index)
      if not box:
        raise Interpreter_error("Index out of range: got {} for array of size {}".format(
                                  index, location.child.location.type_object.size))
      return box
    elif type(location.child) is syntax_tree.Variable:
      return self.environment.get_box(location.child.name)

