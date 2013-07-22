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
  def reset_library(self):
    self.div_by_zero = False
    self.mod_by_zero = False
    self.bad_index = False
    self.write_output = False
    self.read_input = False
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
  def generate_binary(self, binary):
  def generate_division(self, division):
  def generate_compare(self, compare):
  def generate_unconditional_jump(self, jump):
  def generate_conditional_jump(self, jump):
  def generate_call(self, call):
  def generate_write(self, write):
  def generate_read(self, read):
  def generate_bad_index(self, bad_index):
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
