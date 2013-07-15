import syntax_tree
import symbol_table
import code_library

INTEGER_SIZE = 8

class Lazy_generator(object):
  def generate(self, tree, table):
    self.tree = tree
    self.table = table
    self.reset_library() 
    self.handle = -1
    self.in_procedure = False
    self.procedures = {}
    self.read_only_declarations = []
    self.code = ['\t.globl\tmain\n']
    self.code.append('\t.text')
    self.code.append('main:\n')
    if tree:
      self.generate_instructions(tree.instructions)
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
    self.generate_variables()
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
  def generate_instructions(self, instructions):
    for instruction in instructions.instructions:
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
    count = assign.location.type_object.get_size() / INTEGER_SIZE
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
    self.generate_instructions(if_statement.instructions_true)
    if if_statement.instructions_false:
      self.code.append("\t\tjmp\t\t_end_{}_".format(handle))
    self.code.append("_false_{}_:".format(handle))
    if if_statement.instructions_false:
      self.generate_instructions(if_statement.instructions_false)
      self.code.append("_end_{}_:".format(handle))
  def generate_repeat(self, repeat):
    label = "__repeat_at_{}".format(repeat.line)
    self.code.append(label + ':')
    self.generate_condition_evaluator(repeat.condition)
    handle = self.handle
    self.code.append("_false_{}_:".format(handle))
    self.generate_instructions(repeat.instructions)
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
              actual.type_object.get_size() > INTEGER_SIZE):
            self.generate_location_evaluator(actual.child)
          else:
            self.generate_expression_evaluator(actual)
      self.code.append("\t\tcall\t__{}__".format(call.definition.name))
      if not call.definition.name in self.procedures:
        self.procedures[call.definition.name] = call.definition
      if call.definition.formals:
        n = len(call.definition.formals)
        self.code.append("\t\taddq\t${}, %rsp".format(n * INTEGER_SIZE))
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
    self.formals = procedure.formals
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
      self.generate_instructions(procedure.instructions)
    if procedure.return_expression:
      self.generate_expression_evaluator(procedure.return_expression)
      self.code.append('\t\tpopq\t%rax')
    self.in_procedure = False
    self.code.append('\t\tpopq\t%rbx')
    self.code.append('\t\tmovq\t%rbp, %rsp')
    self.code.append('\t\tpopq\t%rbp')
    self.code.append('\t\tret')
  def generate_variables(self):
    symbols = self.table.scopes[1].symbols
    printed_data = False
    for name, type_object in symbols.iteritems():
      if not type(type_object) in [symbol_table.Variable, symbol_table.Array, symbol_table.Record,
                                   symbol_table.Integer]:
          continue
      if not printed_data:
        self.code.append('\n\t.data')
        printed_data = True
      self.code.append("{}_:\t\t.space {}".format(name, type_object.get_size()))
  def generate_condition_evaluator(self, condition):
    self.generate_expression_evaluator(condition.expression_left)
    if not type(condition.expression_right.child) is syntax_tree.Number:
      self.generate_expression_evaluator(condition.expression_right)
      self.code.append('\t\tpopq\t%rcx')
      self.code.append('\t\tpopq\t%rax')
      self.code.append('\t\tcmpq\t%rcx, %rax')
    else:
      self.code.append('\t\tpopq\t%rax')
      value = condition.expression_right.child.table_entry.value
      self.code.append("\t\tcmpq\t${}, %rax".format(value))
    self.new_handle()
    if condition.relation == '=':
      self.code.append("\t\tje\t\t_true_{}_".format(self.handle))
      self.code.append("\t\tjmp\t\t_false_{}_".format(self.handle))
    elif condition.relation == '#':
      self.code.append("\t\tjne\t\t_true_{}_".format(self.handle))
      self.code.append("\t\tjmp\t\t_false_{}_".format(self.handle))
    elif condition.relation == '<':
      self.code.append("\t\tjl\t\t_true_{}_".format(self.handle))
      self.code.append("\t\tjmp\t\t_false_{}_".format(self.handle))
    elif condition.relation == '>':
      self.code.append("\t\tjg\t\t_true_{}_".format(self.handle))
      self.code.append("\t\tjmp\t\t_false_{}_".format(self.handle))
    elif condition.relation == '<=':
      self.code.append("\t\tjle\t\t_true_{}_".format(self.handle))
      self.code.append("\t\tjmp\t\t_false_{}_".format(self.handle))
    else: # >=
      self.code.append("\t\tjge\t\t_true_{}_".format(self.handle))
      self.code.append("\t\tjmp\t\t_false_{}_".format(self.handle))
  def generate_location_evaluator(self, location):
    if type(location.child) is syntax_tree.Field:
      field = location.child
      self.generate_location_evaluator(field.location)
      self.code.append('\t\tpopq\t%rax')
      offset = field.location.type_object.get_offset(field.variable.name)
      self.code.append("\t\taddq\t${}, %rax".format(offset))
      self.code.append('\t\tpushq\t%rax')
    elif type(location.child) is syntax_tree.Index:
      index = location.child
      self.generate_location_evaluator(index.location)
      if not type(index.expression.child) is syntax_tree.Number:
        self.generate_expression_evaluator(index.expression)
        self.code.append('\t\tpopq\t%rcx')
        self.code.append('\t\tpopq\t%rax')
        self.code.append('\t\tcmpq\t$0, %rcx')
        self.new_handle()
        self.code.append("\t\tjl\t\t_error_{}_".format(self.handle))
        self.code.append("\t\tcmpq\t${}, %rcx".format(index.location.type_object.size))
        self.code.append("\t\tjl\t\t_no_error_{}_".format(self.handle))
        self.code.append("_error_{}_:".format(self.handle))
        self.code.append("\t\tmovq\t${}, %rdi".format(index.expression.line))
        self.code.append('\t\tmovq\t%rcx, %rdx')
        self.code.append('\t\tjmp\t\t__error_bad_index')
        self.code.append("_no_error_{}_:".format(self.handle))
        self.code.append("\t\timulq\t${}, %rcx".format(index.type_object.get_size()))
        self.code.append('\t\taddq\t%rcx, %rax')
        self.code.append('\t\tpushq\t%rax')
        self.bad_index = True
      else:
        self.code.append('\t\tpopq\t%rax')
        value = index.expression.child.table_entry.value
        offset = index.location.type_object.get_offset(value)
        self.code.append("\t\taddq\t${}, %rax".format(offset))
        self.code.append('\t\tpushq\t%rax')
    elif not self.in_procedure:
      self.code.append("\t\tmovq\t${}_, %rax".format(location.child.name))
      self.code.append('\t\tpushq\t%rax')
    else:
      variable = location.child
      if variable.name in self.local_variables:
        offset = self.local_variables.index(variable.name) * 8
        if not offset:
          self.code.append('\t\tpushq\t%rbx')
        else:
          self.code.append("\t\tleaq\t{}(%rbx), %rax".format(offset))
          self.code.append('\t\tpushq\t%rax')
      else:
        offset = -1
        n = 2
        if self.formals:
          for formal in self.formals:
            if formal == variable.name:
              offset = 8 * n
              break
            n += 1
        if not offset is -1:
          if location.type_object.get_size() > 8:
            self.code.append("\t\tmovq\t{}(%rbp), %rax".format(offset))
          else:
            self.code.append("\t\tleaq\t{}(%rbp), %rax".format(offset))
        else:
          self.code.append("\t\tmovq\t${}_, %rax".format(variable.name))
        self.code.append('\t\tpushq\t%rax')
  def generate_expression_evaluator(self, expression):
    if type(expression.child) is syntax_tree.Number:
      self.code.append("\t\tpushq\t${}".format(expression.child.table_entry.value))
    elif type(expression.child) is syntax_tree.Location:
      self.generate_location_evaluator(expression.child)
      self.code.append('\t\tpopq\t%rax')
      self.code.append('\t\tmovq\t(%rax), %rcx')
      self.code.append('\t\tpushq\t%rcx')
    elif type(expression.child) is syntax_tree.Binary:
      if expression.child.operator == '+':
        self.generate_addition_like_evaluator(expression.child, 'addq')
      elif expression.child.operator == '-':
        self.generate_addition_like_evaluator(expression.child, 'subq')
      elif expression.child.operator == '*':
        self.generate_addition_like_evaluator(expression.child, 'imulq')
      elif expression.child.operator == 'DIV':
        self.generate_division_evaluator(expression.child, '__error_div_by_zero', '%rax')
      else: # MOD
        self.generate_division_evaluator(expression.child, '__error_mod_by_zero', '%rdx')
    elif type(expression.child) is syntax_tree.Call:
      self.generate_call(expression.child)
      self.code.append('\t\tpushq\t%rax')
  def generate_addition_like_evaluator(self, binary, operation):
    self.generate_expression_evaluator(binary.expression_left)
    if not type(binary.expression_right.child) is syntax_tree.Number:
      self.generate_expression_evaluator(binary.expression_right)
      self.code.append('\t\tpopq\t%rcx')
      self.code.append('\t\tpopq\t%rax')
      self.code.append("\t\t{}\t%rcx, %rax".format(operation))
    else:
      self.code.append('\t\tpopq\t%rax')
      value = binary.expression_right.child.table_entry.value
      self.code.append("\t\t{}\t${}, %rax".format(operation, value))
    self.code.append('\t\tpushq\t%rax')
  def generate_division_evaluator(self, binary, error_function, return_register):
    self.generate_expression_evaluator(binary.expression_left)
    self.generate_expression_evaluator(binary.expression_right)
    self.code.append('\t\tpopq\t%rcx')
    self.code.append('\t\tpopq\t%rax')
    self.new_handle()
    if not type(binary.expression_right.child) is syntax_tree.Number:
      self.code.append('\t\tcmpq\t$0, %rcx')
      self.code.append("\t\tjne\t\t_no_error_{}_".format(self.handle))
      self.code.append("\t\tmovq\t${}, %rdi".format(binary.line))
      self.code.append("\t\tjmp\t\t{}".format(error_function))
      if error_function == '__error_div_by_zero':
        self.div_by_zero = True
      if error_function == '__error_mod_by_zero':
        self.mod_by_zero = True
      self.code.append("_no_error_{}_:".format(self.handle))
    self.code.append('\t\tmovq\t%rax, %rdx')
    self.code.append('\t\tsarq\t$63, %rdx')
    self.code.append('\t\tidivq\t%rcx')
    self.code.append("\t\tpushq\t{}".format(return_register))
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

