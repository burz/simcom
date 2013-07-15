import syntax_tree

class Assign(object):
  def __init__(self, location_value, expression_value):
    self.location_value = location_value
    self.expression_value = expression_value
  def __repr__(self):
    return "Assign: {} -> {}".format(self.expression_value, self.location_value)

class Binary(object):
  def __init__(self, operation, left_value, right_value):
    self.operation = operation
    self.left_value = left_value
    self.right_value = right_value
  def __repr__(self):
    return "Binary({}): {} -> {}".format(self.operation, self.left_value, self.right_value)

class Division(object):
  def __init__(self, left_value, right_value):
    self.left_value = left_value
    self.right_value = right_value
  def __repr__(self):
    return "Division: {} / {}".format(self.left_value, self.right_value)

class Compare(object):
  def __init__(self, left_value, right_value):
    self.left_value = left_value
    self.right_value = right_value
  def __repr__(self):
    return "Compare: {} {}".format(self.left_value, self.right_value)

class Unconditional_jump(object):
  def __init__(self, line):
    self.line = line
  def __repr__(self):
    return "Unconditional Jump: goto {}".format(self.line)

class Conditional_jump(object):
  def __init__(self, operation, line):
    self.operation = operation
    self.line = line
  def __repr__(self):
    return "Conditional Jump: {} goto {}".format(self.operation, self.line)

class Call(object):
  def __init__(self, call):
    self.call = call
  def __repr__(self):
    return "Call: {}".format(self.call.definition.name)

class Write(object):
  def __init__(self, value):
    self.value = value
  def __repr__(self):
    return "Write: {}".format(self.value)

class Read(object):
  def __init__(self, read):
    self.read = read
  def __repr__(self):
    return "Read: {}".format(self.read)

class Label(object):
  def __init__(self):
    pass
  def __repr__(self):
    return "Label: {}".format(id(self))

class Bad_index(object):
  def __init__(self, line, result):
    self.line = line
    self.result = result
  def __repr__(self):
    return "Bad Index: {} {}".format(self.line, self.result)

class Div_by_zero(object):
  def __init__(self, line):
    self.line = line
  def __repr__(self):
    return "Div By Zero: {}".format(self.line)

class Mod_by_zero(object):
  def __init__(self, line):
    self.line = line
  def __repr__(self):
    return "Mod By Zero: {}".format(self.line)

class Intermediate_code_generator(object):
  def generate(self, tree, table):
    self.tree = tree
    self.table = table
    self.lines = []
    self.reset_library()
    self.handle = -1
    self.generate_instructions(tree.instructions)
    return self.lines
  def reset_library(self):
    self.div_by_zero = False
    self.mod_by_zero = False
    self.bad_index = False
    self.write_output = False
    self.read_input = False
  def new_handle(self):
    self.handle += 1
    return self.handle
  def generate_instructions(self, instructions):
    for instruction in instructions.instructions:
      self.generate_instruction(instruction)
  def generate_instruction(self, instruction):
    if type(instruction.child) is syntax_tree.Assign:
      self.generate_assign(instruction.child)
    elif type(instruction.child) is syntax_tree.If:
      self.generate_if(instruction.child)
    elif type(instruction.child) is syntax_tree.Repeat:
      self.generate_repeat(instruction.child)
    elif type(instruction.child) is syntax_tree.Read:
      self.generate_read(instruction.child)
    elif type(instruction.child) is syntax_tree.Call:
      self.generate_call(instruction.child)
    else: # Write
      self.generate_write(instruction.child)
  def generate_assign(self, assign):
    location = self.generate_location_evaluator(assign.location)
    expression = self.generate_expression_evaluator(assign.expression)
    assign = Assign(location, expression)
    self.lines.append(assign)
  def generate_if(self, if_statement):
    left = self.generate_expression_evaluator(if_statement.condition.expression_left)
    right = self.generate_expression_evaluator(if_statement.condition.expression_right)
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
    left = self.generate_expression_evaluator(repeat.condition.expression_left)
    right = self.generate_expression_evaluator(repeat.condition.expression_right)
    compare = Compare(left, right)
    self.lines.append(compare)
    conditional_jump = Conditional_jump(repeat.condition.relation, start)
    self.lines.append(conditional_jump)
  def generate_read(self, read):
    location = self.generate_location_evaluator(read.location)
    read = Read(location)
    self.lines.append(read)
  def generate_call(self, call):
    call = Call(call)
    self.lines.append(call)
  def generate_write(self, write):
    integer = self.generate_expression_evaluator(write.expression)
    write = Write(integer)
    self.lines.append(write)
  def generate_location_evaluator(self, location):
    if type(location.child) is syntax_tree.Field:
      field = location.child
      location = self.generate_location_evaluator(field.location)
      offset = field.location.type_object.get_offset(field.variable.name)
      add = Binary('add', "${}".format(offset), location)
    elif type(location.child) is syntax_tree.Index:
      index = location.child
      location = self.generate_location_evaluator(index.location)
      if not type(index.expression.child) is syntax_tree.Number:
        expression = self.generate_expression_evaluator(index.expression)
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
        bad_index = Bad_index(index.expression.line, expression)
        self.lines += [bad_index, no_error]
        multiply = Binary('mul', "${}".format(index.type_object.get_size()), expression)
        self.lines.append(multiply)
        add = Binary('add', expression, location)
        self.lines.append(add)
        self.bad_index = True
        return location
      else:
        value = index.expression.child.table_entry.value
        offset = index.location.type_object.get_offset(value)
        add = Binary('add', "${}".format(offset), location)
        self.lines.append(add)
        return location
    else:
      return location.child.name
  def generate_expression_evaluator(self, expression):
    if type(expression.child) is syntax_tree.Number:
      self.new_handle()
      temp_var = "!{}".format(self.handle)
      value = expression.child.table_entry.value
      move = Binary('mov', "${}".format(value), temp_var)
      self.lines.append(move)
      return temp_var
    elif type(expression.child) is syntax_tree.Location:
      location = self.generate_location_evaluator(expression.child)
      if not type(expression.child.child) is syntax_tree.Variable:
        self.new_handle()
        temp_var = "!{}".format(self.handle)
        move_mem = Binary('mov_mem', location, temp_var)
        self.lines.add(move_mem)
        return temp_var
      return location
    elif type(expression.child) is syntax_tree.Call:
      self.generate_call(expression.child)
      return '%rax'
    elif type(expression.child) is syntax_tree.Binary:
      if expression.child.operator == '+':
        return self.generate_addition_like_evaluator(expression.child, 'add')
      elif expression.child.operator == '-':
        return self.generate_addition_like_evaluator(expression.child, 'sub')
      elif expression.child.operator == '*':
        return self.generate_addition_like_evaluator(expression.child, 'mul')
      elif expression.child.operator == 'DIV':
        return self.generate_division_evaluator(expression.child)
      else: # MOD
        return self.generate_division_evaluator(expression.child)
  def generate_addition_like_evaluator(self, binary, operation):
    left = self.generate_expression_evaluator(binary.expression_left)
    if not type(binary.expression_right.child) is syntax_tree.Number:
      right = self.generate_expression_evaluator(binary.expression_right)
      binary = Binary(operation, right, left)
      self.lines.append(binary)
    return left
  def generate_division_evaluator(self, binary):
    left = self.generate_expression_evaluator(binary.expression_left)
    right = self.generate_expression_evaluator(binary.expression_right)
    if not type(binary.expression_right.child) is syntax_tree.Number:
      compare = Compare('$0', right)
      self.lines.append(compare)
      no_error = Label()
      conditional_jump = Conditional_jump('#', Label())
      self.lines.append(conditional_jump)
      if binary.operator == 'DIV':
        div_by_zero = Div_by_zero(binary.line)
        self.lines.append(div_by_zero)
        self.div_by_zero = True
      elif binary.operator == 'MOD':
        mod_by_zero = Mod_by_zero(binary.line)
        self.lines.append(mod_by_zero)
        self.mod_by_zero = True
      self.lines.append(no_error)
    div = Division(left, right)
    self.lines.append(div)
    if binary.operator == 'DIV':
      return '%rax'
    elif binary.operator == 'MOD':
      return '%rdx'

