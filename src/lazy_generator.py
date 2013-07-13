import code_library

INTEGER_SIZE = 8

class Code_generator(object):
  def generate(self, table, tree):
    self.table = table
    self.tree = tree
    self.reset_library() 
    self.handle = -1
    self.in_procedure = False
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
  def new_handle(self):
    self.handle += 1
    return self.handle
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
    self.code.append("__assign_at_{}:".format(assign.line))
    self.generate_location_evaluator(assign.location)
    count = assign.location.get_size() / INTEGER_SIZE
    if count is 1:
      self.generate_expression_evaluator(assign.expression)
    else:
      self.generate_location_evaluator(assign.expression.child)
    self.code.append('\t\tpopq\t%rcx')
    self.code.append('\t\tpopq\t%rax')
    if count > 1:
      self.code.append("\t\tmovq\t${}, %rdi".format(count))
      handle = self.new_handle()
      self.code.append("_loop_{}_:".format(handle))
      self.code.append('\t\tmovq\t(%rcx), %rsi')
      self.code.append('\t\tmovq\t%rsi, (%rax)')
      self.code.append('\t\taddq\t$8, %rcx')
      self.code.append('\t\taddq\t$8, %rax')
      self.code.append('\t\tdecq\t%rdi')
      self.code.append("\t\tjnz\t\t_loop_{}_".format(handle))
    else:
      self.code.append('\t\tmovq\t%rcx, (%rax)')
  def generate_if(self, if_statement):
    self.code.append("__if_at_{}:".format(if_statement.line))
    self.generate_condition_evaluator(if_statement.condition)
    handle = self.handle
    self.code.append("_true_{}_:".format(handle))
    self.generate_instructions(if_statement.instructions_true.instructions)
    if if_statement.instructions_false:
      self.code.append("\t\tjmp\t\t_end_{}_".format(handle))
    self.code.append("_false_{}_:".format(handle))
    if if_statement.instructions_false:
      self.generate_instructions(if_statement.instructions_false.instructions)
      self.code.append("_end_{}_:".format(handle))
  def generate_repeat(self, repeat):
    label = "__repeat_at_{}".format(repeat.line)
    self.code.append(label + ':')
    self.generate_condition_evaluator(repeat.condition)
    handle = self.handle
    self.code.append("_false_{}_:".format(handle))
    self.generate_instructions(repeat.instructions.instructions)
    self.code.append("\t\tjmp\t\t{}".format(label))
    self.code.append("_true_{}_:".format(handle))
  def generate_read(self, read):
    self.code.append("__read_at_{}:".format(read.line))
    self.code.append('\t\tpushq\t%rbx')
    self.generate_location_evaluator(read.location)
    self.code.append('\t\tpopq\t%rbx')
    self.code.append('\t\tcall\t__read')
    self.code.append('\t\tmovq\t%rax, (%rbx)')
    self.code.append('\t\tpopq\t%rbx')
    self.read_input = True
  def generate_call(self, call):
    if call.definition.instructions or call.definition.return_expression:
      if call.actuals:
        for actual in call.actuals:
          if (type(actual.child) is syntax_tree.Location and
              actual.child.get_size() > INTEGER_SIZE):
            self.generate_location_evaluator(actual.child)
          else:
            self.generate_expression_evaluator(actual)
      self.code.append("\t\tcall\t__{}__".format(call.definition.name))
      if not call.definition.name in self.procedures:
        self.procedures[call.definition.name] = call.definition
      if call.definition.formals:
        number = len(call.definition.formals)
        self.code.append("\t\taddq\t${}, %rsp".format(times * INTEGER_SIZE))
  def generate_write(self, write):
    self.code.append("__write_at_{}:".format(write.line))
    self.generate_expression_evaluator(write.expression)
    self.code.append('\t\tpopq\t%rdi')
    self.code.append('\t\tcall\t__write_stdout')
    self.write_output = True
  def generate_procedure(self, procedure):
    self.code.append("__{}__:".format(procedure.name))
    self.code.append('\t\tpushq\t%rbp')
    self.code.append('\t\tmovq\t%rsp, %rbp')
    self.in_procedure = True
    self.formals = procedure.formals:
    self.local_variables = []
    offset = 0
    for variable in procedure.scope.symbols:
      if not self.formals or not variable in self.formals:
        self.local_variables.append(variable)
        offset += procedure.scope.symbols[variable].get_size()
    times = offset / 8
    for i in range(times):
      self.code.append('\t\tpushq\t$0')
    self.code.append('\t\tpushq\t%rbx')
    self.code.append('\t\tleaq\t8(%rsp), %rbx')
    if procedure.instructions:
      self.generate_instructions(procedure.instructions.instructions)
    if procedure.return_expression:
      self.generate_expresssion_evaluator(procedure.return_expression)
      self.code.append('\t\tpopq\t%rax')
    self.in_procedure = False
    self.code.append('\t\tpopq\t%rbx')
    self.code.append('\t\tmovq\t%rbp, %rsp')
    self.code.append('\t\tpopq\t%rbp')
    self.code.append('\t\tret')
  def generate_variables(self):
    self.code.append('\n\n.data')
    for name, type_object in self.symbol_table.scopes[1].symbols.iteritems():
      if not type(type_object) is symbol_table.Variable:
        continue
      self.code.append("{}_:\t\t.space {}".format(name, type_object.get_size()))
  def generate_location_evaluator(self, location):
  def generate_condition_evaluator(self, condition):
  def generate_expression_evaluator(self, expression):
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

