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
  def __init__(self, procedure):
    self.procedure = procedure

class Label(object):
  def __init__(self):
    pass

class Intermediate_code_generator(object):
  def generate(self, tree, table):
    self.tree = tree
    self.table = table
    self.lines = []
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
    c = Compare(left, right)
    self.lines.append(c)
    label = Label()
    cj = Conditional_jump('jne', label)
    self.lines += [cj, label]
  def generate_repeat(self, repeat):
  def generate_read(self, read):
  def generate_call(self, call):
  def generate_write(self, write):

