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
    self.div_by_zero = False
    self.mod_by_zero = False
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
  def generate_variables(self):
    self.code.append('\n\n.data')
    for name, type_object in self.symbol_table.scopes[1].symbols.iteritems():
      if not type(type_object) is symbol_table.Variable:
        continue
      self.code.append("{}_:\t\t.space {}".format(name, type_object.get_size()))
  def link_library(self):
    evaluated_to_zero = False
    stderr_printing = False
    write_code = False
    if self.div_by_zero:
      self.code.append(code_library.error_div_zero)
      decl = '_div_error:\t\t.ascii "error: The right side of the DIV expression at ("'
      self.read_only_declarations.append(decl)
      evaluated_to_zero = True
      stderr_printing = True
    if self.mod_by_zero:
      self.code.append(code_library.error_mod_zero)
      decl = '_mod_error:\t\t.ascii "error: The right size of the MOD expression at ("'
      self.read_only_declarations.append(decl)
    if evaluated_to_zero:
      self.read_only_declarations.append('_zero_end:\t\t.ascii ") evaluated to zero\\n"')
    if self.bad_index:
      self.code.append(code_library.error_index_range_code)
      decl = '_index_range:\t.ascii "error: Index out of range: the expression at ("'
      self.read_only_declarations.append(decl)
      self.read_only_declarations.append('_evaluated_to:\t.ascii ") evaluated to "')
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
      self.code.append(code_library.error_input)
      decl = '_bad_input:\t\t.ascii "error: The input was not an integer\\n"'
      self.read_only_declarations.append(decl)

