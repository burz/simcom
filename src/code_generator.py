registers = ['%rax', '%rcx', '%rdx', '%rsi', '%rdi', '%r8', '%r9', '%r10', '%r11']

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

class Code_generator(object):
  def generate(self, flow_graph):
    self.flow_graph = flow_graph
    self.descriptors = Location_descriptors()
    self.code = []
    self.generate_block(flow_graph.start)
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
  def generate_mod_by_zero(self, mod_by_zero):

