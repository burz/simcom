import symbol_table

INTEGER_SIZE = 8

registers = ['%rax', '%rcx', '%rdx', '%rsi', '%rdi', '%r8', '%r9', '%r10', '%r11']
callee_registers = ['%rbx', '%r12', '%r13', '%r14', '%r15']

class Location_descriptors(object):
  def __init__(self):
    self.registers = {}
    for register in registers
      self.registers[register] = []
    self.addresses = {}
  def get_register_descriptor(self, register):
    return self.registers[register]
  def get_address_descriptor(self, address):
    if not address in self.addresses:
      self.addresses[address] = []
    return self.addresses[address]
  def clear_register_decriptor(self, register):
    self.registers[register] = []
  def clear_address_descriptor(self, address):
    self.addresses[address] = []
  def empty_register(self):
    for register in self.registers:
      if not self.registers[register]:
        return register
    return False
  def get_registers(self, left, right, no_assign = False):
    left_register, code = get_left_register(left)
    if no_assign:
      right_register, new_code = get_left_register(right)
    else:
      right_register, new_code = get_right_register(right)
    return left_register, right_register, code + new_code
  def get_left_register(self, left):
  def get_right_register(self, right):

class Code_generator(object):
  def generate(self, flow_graph):
    self.flow_graph = flow_graph
    self.descriptors = Location_descriptors()
    self.code = []
    self.read_only_declarations = []
    self.generate_block(flow_graph.start)
    self.reset_library()
    self.handle = -1
  def reset_library(self):
    self.div_by_zero = False
    self.mod_by_zero = False
    self.bad_index = False
    self.write_output = False
    self.read_input = False
  def new_handle(self):
    self.handle += 1
    return self.handle
  def generate_block(self, block):
    for line in block.lines:
      self.generate_line(line)
  def generate_line(self, line):
    if type(line) is intermediate_code_generator.Assign:
      self.generate_assign(line)
    elif type(line) is intermediate_code_generator.Binary:
      self.generate_binary(line)
    elif type(line) is intermediate_code_generator.Division:
      self.generate_division(line)
    elif type(line) is intermediate_code_generator.Compare:
      self.generate_compare(line)
    elif type(line) is intermediate_code_generator.Unconditional_jump:
      self.generate_unconditional_jump(line)
    elif type(line) is intermediate_code_generator.Conditinal_jump:
      self.generate_conditional_jump(line)
    elif type(line) is intermediate_code_generator.Call:
      self.generate_call(line)
    elif type(line) is intermediate_code_generator.Write:
      self.generate_write(line)
    elif type(line) is intermediate_code_generator.Read:
      self.generate_read(line)
    elif type(line) is intermediate_code_generator.Bad_index:
      self.generate_bad_index(line)
    elif type(line) is intermediate_code_generator.Div_by_zero:
      self.generate_div_by_zero(line)
    elif type(line) is intermediate_code_generator.Mod_by_zero:
      self.generate_mod_by_zero(line)
  def generate_assign(self, assign):
# Implement aliasing
    location, expression = self.descriptors.get_registers(assign.location_value,
                                                          assign.expression_value)
    if assign.type_object is symbol_table.Integer:
      self.code.append("\t\tmovq\t{}, {}".format(expression, location))
    else:
      n = assign.type_object.get_size() / INTEGER_SIZE
      handle = self.new_handle()
      temp_register = self.get_right_register()
      count_register = self.get_right_register()
      self.code.append("\t\tmovq ${}, {}".format(n, count_register))
      self.code.append("_assign_loop_{}".format(handle))
      self.code.append("\t\tmovq\t({}), {}".format(expression, temp_register))
      self.code.append("\t\tmovq\t{}, ({})".format(temp_register, location))
      self.code.append("\t\tsubq\t$1, {}".format(count_register))
      self.code.append("\t\tjz\t\t_end_assign_loop_{}".format(handle))
      self.code.append("\t\taddq\t${}, {}".format(INTEGER_SIZE, expression))
      self.code.append("\t\taddq\t${}, {}".format(INTEGER_SIZE, location))
      self.code.append("\t\tjmp\t\t_assign_loop_{}".format(handle)
      self.code.append("_end_assign_loop_{}:")
  def generate_binary(self, binary):
    left, right = self.descriptors.get_registers(binary.left_value, binary.right_value)
    if binary.operation == 'mov_mem':
      self.code.append("\t\tmovq\t({}), {}".format(left, right))
    else:
      self.code.append("\t\t{}\t{}, {}".format(binary.operation, left, right))
  def generate_division(self, division):
# Clear register descriptors for %rax and %rdx
    left, right = self.descriptors.get_registers(division.left_value, division.right_value)
    self.code.append("\t\tidivq\t{}, {}".format(left, right))
  def generate_compare(self, compare):
    left, right = self.descriptors.get_registers(compare.left_value, compare.right_value)
    self.code.append("\t\tcmpq\t{}, {}".format(left, right))
  def generate_unconditional_jump(self, jump):
    self.code.append("\t\tjmp\t\t__block__{}".format(jump.block.block_id))
  def generate_conditional_jump(self, jump):
    if jump.operation == '=':
      self.code.append("\t\tje\t\t__block__{}".format(jump.block.block_id))
    elif jump.operation == '#':
      self.code.append("\t\tjne\t\t__block__{}".format(jump.block.block_id))
    elif jump.operation == '<':
      self.code.append("\t\tjl\t\t__block__{}".format(jump.block.block_id))
    elif jump.operation == '>':
      self.code.append("\t\tjg\t\t__block__{}".format(jump.block.block_id))
    elif jump.operation == '<=':
      self.code.append("\t\tjle\t\t__block__{}".format(jump.block.block_id))
    else: # >=
      self.code.append("\t\tjge\t\t__block__{}".format(jump.block.block_id))
  def generate_call(self, call):
# reset register descriptors
    self.code.append("\t\tcall\t_function_{}".format(call.call.defintion.name))
  def generate_write(self, write):
# reset register descriptors
    register = self.get_left_register(write.value)
    if not register[0] == '$' and register == '%rdi':
      self.code.append("\t\tmovq\t{}, %rdi".format(register))
    self.code.append('\t\tcall\t__write_stdout')
    self.write_output = True
  def generate_read(self, read):
# reset register descriptors
# mark %rax as holding >%rax
  def generate_bad_index(self, bad_index):
    result = self.get_left_register(bad_index.expression)
    self.code.append("\t\tmovq\t${}, %rdi".format(bad_index.line))
    self.code.append("\t\tmovq\t{}, %rdx".format(result))
    self.code.append('\t\tjmp\t\t__error_bad_index')
    self.bad_index = True
  def generate_div_by_zero(self, div_by_zero):
    self.code.append("\t\tmovq\t${}, %rdi".format(div_by_zero.line))
    self.code.append('\t\tjmp\t\t__error_div_by_zero')
    self.div_by_zero = True
  def generate_mod_by_zero(self, mod_by_zero):
    self.code.append("\t\tmovq\t${}, %rdi".format(mod_by_zero.line))
    self.code.append('\t\tjmp\t\t__error_mod_by_zero')
    self.mod_by_zero = True
  def link_library(self):
    evaluated_to_zero = False
    stderr_printing = False
    write_code = False
    if self.div_by_zero:
      self.code.append(code_library.error_div_by_zero_code)
      decl = '_div_error:\t\t.ascii "error: The right side of the DIV expression on line "'
      self.read_only_declarations.append(decl)
      evaluated_to_zero = True
      stderr_printing = True
    if self.mod_by_zero:
      self.code.append(code_library.error_mod_by_zero_code)
      decl = '_mod_error:\t\t.ascii "error: The right size of the MOD expression on line "'
      self.read_only_declarations.append(decl)
      evaluated_to_zero = True
      stderr_printing = True
    if evaluated_to_zero:
      self.read_only_declarations.append('_zero_end:\t\t.ascii ") evaluated to zero\\n"')
    if self.bad_index:
      self.code.append(code_library.error_bad_index_code)
      decl = '_index_range:\t.ascii "error: Index out of range: the expression on line "'
      self.read_only_declarations.append(decl)
      self.read_only_declarations.append('_evaluated_to:\t.ascii " evaluated to "')
      stderr_printing = True
    if self.write_output:
      self.code.append(code_library.write_stdout_code)
      write_code = True
    if stderr_printing:
      self.code.append(code_library.write_stderr_code)
      write_code = True
    if write_code:
      self.code.append(code_library.write_code)
    if self.read_input:
      self.code.append(code_library.read_code)
      self.code.append(code_library.error_bad_input_code)
      decl = '_bad_input:\t\t.ascii "error: The input was not an integer\\n"'
      self.read_only_declarations.append(decl)

