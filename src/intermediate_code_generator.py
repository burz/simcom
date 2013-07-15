import symbol_table

class Assign(object):
  def __init__(self, left_value, right_value):
    self.left_value = left_value
    self.right_value = right_value

class Binary(object):
  def __init__(self, operation, left_value, right_value):
    self.operation = operation
    self.left_value = left_value
    self.right_value = right_value

class Division(object):
  def __init__(self, left_value, right_value):
    self.left_value = left_value
    self.right_value = right_value

class Compare(object):
  def __init__(self, left_value, right_value):
    self.left_value = left_value
    self.right_value = right_value

class Unconditional_jump(object):
  def __init__(self, line):
    self.line = line

class Conditional_jump(object):
  def __init__(self, operation, line):
    self.operation = operation
    self.line = line

class Call(object):
  def __init__(self, procedure, library = False):
    self.procedure = procedure
    self.library = library

class Write(object):
  def __init__(self, value):
    self.value = value

class Label(object):
  def __init__(self):
    pass

class Intermediate_code_generator(object):
  def generate(self, tree, table):
    self.tree = tree
    self.table = table
    self.lines = []
    self.reset_library()
  def reset_library(self):
    self.div_by_zero = False
    self.mod_by_zero = False
    self.bad_index = False
    self.write_output = False
    self.read_input = False
  def generate_instructions(self, instructions):
    for instruction in instruction:
      self.generate_instruction(instruction)
  def generate_instruction(self, instruction):
    if type(instruction.child) is symbol_table.Assign:
      self.generate_assign(instruction.child)
    elif type(instruction.child) is symbol_table.If:
      self.generate_if(instruction.child)
    elif type(instruction.child) is symbol_table.Repeat:
      self.generate_repeat(instruction.child)
    elif type(instruction.child) is symbol_table.Read:
      self.generate_read(instruction.child)
    elif type(instruction.child) is symbol_table.Call:
      self.generate_call(instruction.child)
    else: # Write
      self.generate_write(instruction.child)
  def generate_assign(self, assign):
  def generate_if(self, if_statement):
    left = self.generate_expression_evaluator(if_statement.condition.left_expression)
    right = self.generate_expression_evaluator(if_statement.condition.right_expression)
    compare = Compare(left, right)
    self.lines.append(c)
    false = Label()
    conditional_jump = Conditional_jump(if_statement.condition.relation, false)
    self.lines.append(conditional_jump)
    self.generate_instructions(if_statement.instructions_true)
    if if_statement.instructions_false:
      end = Label()
      unconditional_jump = Unconditional_jump(end)
      self.lines.append(unconditional_jump)
    self.lines.append(false)
    if if_statement.instructions_false:
      self.generate_instructions(if_statement.instructions_false)
      self.lines.append(end)
  def generate_repeat(self, repeat):
    start = Label()
    self.lines.append(start)
    self.generate_instructions(repeat.instructions)
    left = self.generate_expression_evaluator(repeat.condition.left_expression)
    right = self.generate_expression_evaluator(repeat.condition.right_expression)
    compare = Compare(left, right)
    self.lines.append(compare)
    conditional_jump = Conditional_jump(repeat.condition.relation, start)
    self.lines.append(conditional_jump)
  def generate_read(self, read):
    call = Call('__read', True)
    self.lines.append(call)
  def generate_call(self, call):
  def generate_write(self, write):
    integer = self.generate_expression_evaluator(write.expression)
    write = Write(integer)
  def generate_location_evaluator(self, location):
  def generate_expression_evaluator(self, expression):

