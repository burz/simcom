import syntax_tree
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
  def __init__(self, call):
    self.call = call

class Write(object):
  def __init__(self, value):
    self.value = value

class Read(object):
  def __init__(self, read):
    self.read = read

class Label(object):
  def __init__(self):
    pass

class Bad_index(object):
  def __init__(self, line, result):
    self.line = line
    self.result = result

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
    location = self.generate_location_evaluator(assign.location)
    expression = self.generate_expression_evaluator(assign.expression)
    assign = Assign(location, expression)
    self.lines.append(assign)
  def generate_if(self, if_statement):
    left = self.generate_expression_evaluator(if_statement.condition.left_expression)
    right = self.generate_expression_evaluator(if_statement.condition.right_expression)
    compare = Compare(left, right)
    self.lines.append(compare)
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
    read = Read(read)
    self.lines.append(read)
  def generate_call(self, call):
    call = Call(call)
  def generate_write(self, write):
    integer = self.generate_expression_evaluator(write.expression)
    write = Write(integer)
  def generate_location_evaluator(self, location):
    if type(location.child) is syntax_tree.Index:
      field = location.child
      location = self.generate_location_evaluator(field.location)
      offset = field.location.type_object.get_offset(field.variable.name)
      add = Binary('add', "${}".format(offset), location)
    elif type(location.child) is syntax_tree.Index:
      index = location.child
      location = self.generate_location_evaluator(self, index.location)
      if not type(index.expression.child) is syntax_tree.Number:
        expression = self.generate_expression_evaluator(self, index.expression)
        compare = Compare('$0', expression)
        self.lines.append(compare)
        error = Label()
        conditional_jump = Conditional_jump('<', error)
        self.lines.append(conditional_jump)
        compare = Compare("${}".format(index.location.type_object.size), expression)
        self.lines.append(compare)
        no_error = Label()
        conditional_jump = Conditional_jump('<', no_error)
        self.lines += [conditional_jump, error]
        index_error = Index_error(index.expression.line, expression)
        self.code += [index_error, no_error]
        multiply = Binary('mul', "${}".format(index.type_object.get_size()), expression)
        self.code.append(multiply)
        add = Binary('add', expression, location)
        self.code.append(add)
        self.bad_index = True
        return location
      else:
        value = index.expression.child.table_entry.value
        offset = index.location.type_object.get_offset(value)
        add = Binary('add', "${}".format(offset), location)
        self.code.append(add)
        return location
    else:
      return location.child.name
  def generate_expression_evaluator(self, expression):

