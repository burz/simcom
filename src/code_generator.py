import code_library

class Code_generator(object):
  def generate(self, table, tree):
    self.table = table
    self.tree = tree
    self.reset_library() 
    self.procedures = {}
    self.read_only_declarations = []
    self.code = ['\t.globl\tmain\n']
    self.code.append('\t.text')
    self.code.append('main:\n')
    if tree:
      self.generate_instructions(tree)
    self.code.append('__end_program:')
    self.code.append('\t\tmovq\t$60, %rax')
    self.code.append('\t\tsyscall\n')
    printed = []
    while self.procedures:
      to_print = self.procedures
      self.procedures = {}
      for procedure in to_print.values():
        if not procedure in printed:
          self.generate_procedure(procedure)
          printed.append(procedure)
    self.link_library()
    if self.table.scopes[1].symbols:
      self.create_variables()
    if self.read_only_declarations:
      self.code.append('\n\t.section .rodata')
      for declaration in self.read_only_declarations:
        self.code.append(declaration)
    return self.code
  def reset_library(self):
    self.mod_by_zero = False
    self.div_by_zero = False
    self.bad_index = False
    self.write_output = False
    self.read_input = False
  def generate_instructions(tree):
    for instruction in tree.instructions.instructions:
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
  def generate_if(self, if_statement):
  def generate_repeat(self, repeat):
  def generate_read(self, read):
  def generate_call(self, call):
  def generate_write(self, write):
  def generate_procedure(self, prcedure):
  def link_library(self):
  def generate_variables(self):

