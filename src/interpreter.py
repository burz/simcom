import syntax_tree
import symbol_table
import environment

class Interpreter_error(Exception):
  def __init__(self, error):
    self.error = error
  def __str__(self):
    return "error: {}".format(self.error)

class Interpreter(object):
  def run(self, tree, table):
    self.program_environment = environment.Environment(table.scopes[1])
    self.environment = self.program_environment
    self.tree = tree
    for instruction in self.tree.instructions.instructions:
      self.do_instruction(instruction)
  def do_instruction(self, instruction):
    if type(instruction.child) is syntax_tree.Assign:
      self.do_assign(instruction.child)
    elif type(instruction.child) is syntax_tree.If:
      self.do_if(instruction.child)
    elif type(instruction.child) is syntax_tree.Repeat:
      self.do_repeat(instruction.child)
    elif type(instruction.child) is syntax_tree.Read:
      self.do_read(instruction.child)
    elif type(instruction.child) is syntax_tree.Call:
      self.do_call(instruction.child)
    else: # Write
      self.do_write(instruction.child)
  def do_assign(self, assign):
    box = self.get_box(assign.location)
    if type(assign.expression.child) is syntax_tree.Location:
      box.set_to(self.get_box(assign.expression.child))
    else:
      box.value = self.evaluate_expression(assign.expression)
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
        self.do_instruction(instruction)
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
    new_environment = environment.Environment(call.definition.scope, self.program_environment)
    if call.actuals:
      for i, actual in enumerate(call.actuals):
        if type(actual.type_object) is symbol_table.Integer:
          new_environment.boxes[call.definition.formals[i]
                               ].value = self.evaluate_expression(actual)
        else:
          new_environment.boxes[call.definition.formals[i]] = self.get_box(actual.child)
    old_environment = self.environment
    self.environment = new_environment
    if call.definition.instructions:
      for instruction in call.definition.instructions.instructions:
        self.do_instruction(instruction)
    if call.definition.return_expression:
      result = self.evaluate_expression(call.definition.return_expression)
      self.environment = old_environment
      return result
    self.environment = old_environment
  def do_write(self, write):
    print self.evaluate_expression(write.expression)
  def evaluate_expression(self, expression):
    if type(expression.child) is syntax_tree.Number:
      return expression.child.table_entry.value
    elif type(expression.child) is syntax_tree.Location:
      if type(expression.child.child) is syntax_tree.Number:
        return expression.child.child.table_entry.value
      return self.get_box(expression.child).value
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
      return record_box.get_box(location.child.variable.name)
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

