import symbol_table
import ast
import code_library

integer_size = 8

class Code_generator(object):
  def __init__(self, table, tree):
    self.table = table
    self.tree = tree
  def _create_location_evaluator(self, location):
    if type(location.child) is ast.Field:
      self._create_location_evaluator(location.child.location)
      self.code.append("\t\tpopq\t%rax")
      if type(location.child.location.child) is ast.Field:
        offset = location.child.location.child.variable.table_entry.type_object.get_offset(location.child.variable.name)
      elif type(location.child.location.child) is ast.Index:
        offset = location.child.location.child.table_entry.get_offset(location.child.variable.name)
      else: # Variable
        offset = location.child.location.child.table_entry.type_object.get_offset(location.child.variable.name)
      self.code.append("\t\taddq\t${}, %rax".format(offset))
      self.code.append("\t\tpushq\t%rax")
    elif type(location.child) is ast.Index:
      self._create_location_evaluator(location.child.location)
      if not type(location.child.expression.child) is ast.Number:
        self._create_expression_evaluator(location.child.expression)
        self.code.append("\t\tpopq\t%rcx")
        self.code.append("\t\tpopq\t%rax")
        self.code.append("\t\tcmpq\t$0, %rcx")
        self.code.append("\t\tjl\t\t_error{}_".format(self.node))
        self.code.append("\t\tcmpq\t${}, %rcx".format(location.child.table_entry.length))
        self.code.append("\t\tjl\t\t_no_error{}_".format(self.node))
        self.code.append("_error{}_:".format(self.node))
        self.code.append("\t\tmovq\t${}, %rdi".format(location.child.expression.start_position))
        self.code.append("\t\tmovq\t${}, %rsi".format(location.child.expression.end_position))
        self.code.append("\t\tmovq\t%rcx, %rdx")
        self.code.append("\t\tjmp\t\t__error_index_range")
        self.code.append("_no_error{}_:".format(self.node))
        self.code.append("\t\timulq\t${}, %rcx".format(location.child.table_entry.get_offset()))
        self.code.append("\t\taddq\t%rcx, %rax")
        self.code.append("\t\tpushq\t%rax")
        self.node += 1
        self.index_range = True
      else:
        self.code.append("\t\tpopq\t%rax")
        offset = location.child.table_entry.get_offset() * location.child.expression.child.table_entry.value
        self.code.append("\t\taddq\t${}, %rax".format(offset))
        self.code.append("\t\tpushq\t%rax")
    else:
      if not self.in_procedure:
        self.code.append("\t\tmovq\t${}_, %rax".format(location.child.name))
        self.code.append("\t\tpushq\t%rax")
      else:
        if location.child.name in self.local_variables:
          offset = self.local_variables.keys().index(location.child.name) * 8
          if not offset:
            self.code.append("\t\tpushq\t%rbx")
          else:
            self.code.append("\t\tleaq\t{}(%rbx), %rax".format(offset))
            self.code.append("\t\tpushq\t%rax")
          return
        offset = -1
        n = 2
        if self.formals:
          for formal in self.formals:
            if formal[0].data == location.child.name:
              offset = 8 * n
              break
            n += 1
        if not offset is -1:
          if location.get_size() > integer_size:
            self.code.append("\t\tmovq\t{}(%rbp), %rax".format(offset))
          else:
            self.code.append("\t\tleaq\t{}(%rbp), %rax".format(offset))
        else:
          self.code.append("\t\tmovq\t${}_, %rax".format(location.child.name))
        self.code.append("\t\tpushq\t%rax")
  def _create_expression_evaluator(self, expression):
    if type(expression.child) is ast.Number:
      self.code.append("\t\tpushq\t${}".format(expression.child.table_entry.value))
    elif type(expression.child) is ast.Location:
      self._create_location_evaluator(expression.child)
      self.code.append("\t\tpopq\t%rax")
      self.code.append("\t\tmovq\t(%rax), %rcx")
      self.code.append("\t\tpushq\t%rcx")
    elif type(expression.child) is ast.Binary:
      self._create_expression_evaluator(expression.child.expression_left)
      if expression.child.operator.data == "+":
        if not type(expression.child.expression_right.child) is ast.Number:
          self._create_expression_evaluator(expression.child.expression_right)
          self.code.append("\t\tpopq\t%rcx")
          self.code.append("\t\tpopq\t%rax")
          self.code.append("\t\taddq\t%rcx, %rax")
        else:
          self.code.append("\t\tpopq\t%rax")
          value = expression.child.expression_right.child.table_entry.value
          self.code.append("\t\taddq\t${}, %rax".format(value))
        self.code.append("\t\tpushq\t%rax")
      elif expression.child.operator.data == "-":
        if not type(expression.child.expression_right.child) is ast.Number:
          self._create_expression_evaluator(expression.child.expression_right)
          self.code.append("\t\tpopq\t%rcx")
          self.code.append("\t\tpopq\t%rax")
          self.code.append("\t\tsubq\t%rcx, %rax")
        else:
          self.code.append("\t\tpopq\t%rax")
          value = expression.child.expression_right.child.table_entry.value
          self.code.append("\t\tsubq\t${}, %rax".format(value))
        self.code.append("\t\tpushq\t%rax")
      elif expression.child.operator.data == "*":
        if not type(expression.child.expression_right.child) is ast.Number:
          self._create_expression_evaluator(expression.child.expression_right)
          self.code.append("\t\tpopq\t%rcx")
          self.code.append("\t\tpopq\t%rax")
          self.code.append("\t\timulq\t%rcx, %rax")
        else:
          self.code.append("\t\tpopq\t%rax")
          value = expression.child.expression_right.child.table_entry.value
          self.code.append("\t\timulq\t${}, %rax".format(value))
        self.code.append("\t\tpushq\t%rax")
      elif expression.child.operator.data == "DIV":
        self._create_expression_evaluator(expression.child.expression_right)
        self.code.append("\t\tpopq\t%rcx")
        self.code.append("\t\tpopq\t%rax")
        if not type(expression.child.expression_right.child) is ast.Number:
          self.code.append("\t\tcmpq\t$0, %rcx")
          self.code.append("\t\tjne\t\t_no_error{}_".format(self.node))
          self.code.append("\t\tmovq\t${}, %rdi".format(expression.start_position))
          self.code.append("\t\tmovq\t${}, %rsi".format(expression.end_position))
          self.code.append("\t\tjmp\t\t__error_div_zero")
          self.code.append("_no_error{}_:".format(self.node))
          self.node += 1
          self.div_zero = True
        self.code.append("\t\tmovq\t%rax, %rdx")
        self.code.append("\t\tsarq\t$63, %rdx")
        self.code.append("\t\tidivq\t%rcx")
        self.code.append("\t\tpushq\t%rax")
      else: # MOD
        self._create_expression_evaluator(expression.child.expression_right)
        self.code.append("\t\tpopq\t%rcx")
        self.code.append("\t\tpopq\t%rax")
        if not type(expression.child.expression_right.child) is ast.Number:
          self.code.append("\t\tcmpq\t$0, %rcx")
          self.code.append("\t\tjne\t\t_no_error{}_".format(self.node))
          self.code.append("\t\tmovq\t${}, %rdi".format(expression.start_position))
          self.code.append("\t\tmovq\t${}, %rsi".format(expression.end_position))
          self.code.append("\t\tjmp\t\t__error_mod_zero")
          self.code.append("_no_error{}_:".format(self.node))
          self.node += 1
          self.mod_zero = True
        self.code.append("\t\tmovq\t%rax, %rdx")
        self.code.append("\t\tsarq\t$63, %rdx")
        self.code.append("\t\tidivq\t%rcx")
        self.code.append("\t\tpushq\t%rdx")
    elif type(expression.child) is ast.Call:
      self._create_call(expression.child)
      self.code.append("\t\tpushq\t%rax")
  def _create_condition_evaluator(self, condition):
    self._create_expression_evaluator(condition.expression_left)
    if not type(condition.expression_right.child) is ast.Number:
      self._create_expression_evaluator(condition.expression_right)
      self.code.append("\t\tpopq\t%rcx")
      self.code.append("\t\tpopq\t%rax")
      self.code.append("\t\tcmpq\t%rcx, %rax")
    else:
      self.code.append("\t\tpopq\t%rax")
      self.code.append("\t\tcmpq\t${}, %rax".format(condition.expression_right.child.table_entry.value))
    if condition.relation.data == "=":
      self.code.append("\t\tje\t\t_true{}_".format(self.node))
      self.code.append("\t\tjmp\t\t_false{}_".format(self.node))
    elif condition.relation.data == "#":
      self.code.append("\t\tjne\t\t_true{}_".format(self.node))
      self.code.append("\t\tjmp\t\t_false{}_".format(self.node))
    elif condition.relation.data == "<":
      self.code.append("\t\tjl\t\t_true{}_".format(self.node))
      self.code.append("\t\tjmp\t\t_false{}_".format(self.node))
    elif condition.relation.data == ">":
      self.code.append("\t\tjg\t\t_true{}_".format(self.node))
      self.code.append("\t\tjmp\t\t_false{}_".format(self.node))
    elif condition.relation.data == "<=":
      self.code.append("\t\tjle\t\t_true{}_".format(self.node))
      self.code.append("\t\tjmp\t\t_false{}_".format(self.node))
    else: # >=
      self.code.append("\t\tjge\t\t_true{}_".format(self.node))
      self.code.append("\t\tjmp\t\t_false{}_".format(self.node))
  def _create_assign(self, instruction):
    self.code.append("__assign_at_{}_{}:".format(instruction.start_position, instruction.end_position))
    self._create_location_evaluator(instruction.location)
    count = instruction.location.get_size() / integer_size
    if count is 1:
      self._create_expression_evaluator(instruction.expression)
    else:
      self._create_location_evaluator(instruction.expression.child)
    self.code.append("\t\tpopq\t%rcx")
    self.code.append("\t\tpopq\t%rax")
    if count > 1:
      self.code.append("\t\tmovq\t${}, %rdi".format(count))
      self.code.append("_loop{}_:".format(self.node))
      self.code.append("\t\tmovq\t(%rcx), %rsi")
      self.code.append("\t\tmovq\t%rsi, (%rax)")
      self.code.append("\t\taddq\t$8, %rcx")
      self.code.append("\t\taddq\t$8, %rax")
      self.code.append("\t\tdecq\t%rdi")
      self.code.append("\t\tjnz\t\t_loop{}_".format(self.node))
      self.node += 1
    else:
      self.code.append("\t\tmovq\t%rcx, (%rax)")
  def _create_if(self, instruction):
    self.code.append("__if_at_{}_{}:".format(instruction.start_position, instruction.end_position))
    self._create_condition_evaluator(instruction.condition)
    self.code.append("_true{}_:".format(self.node))
    node_number = self.node
    self.node += 1
    self._generate_instructions(instruction.instructions_true.get_instructions())
    if instruction.instructions_false:
      self.code.append("\t\tjmp\t\t_end{}_".format(node_number))
    self.code.append("_false{}_:".format(node_number))
    if instruction.instructions_false:
      self._generate_instructions(instruction.instructions_false.get_instructions())
      self.code.append("_end{}_:".format(node_number))
  def _create_repeat(self, instruction):
    label = "__repeat_at_{}_{}".format(instruction.start_position, instruction.end_position)
    self.code.append(label + ":")
    self._create_condition_evaluator(instruction.condition)
    self.code.append("_false{}_:".format(self.node))
    node_number = self.node
    self.node += 1
    self._generate_instructions(instruction.instructions.get_instructions())
    self.code.append("\t\tjmp\t\t{}".format(label))
    self.code.append("_true{}_:".format(node_number))
  def _create_read(self, instruction):
    self.code.append("__read_at_{}_{}:".format(instruction.start_position, instruction.end_position))
    self.code.append("\t\tpushq\t%rbx")
    self._create_location_evaluator(instruction.location)
    self.code.append("\t\tpopq\t%rbx")  
    self.code.append("\t\tcall\t__read")
    self.code.append("\t\tmovq\t%rax, (%rbx)")
    self.code.append("\t\tpopq\t%rbx")
    self.read_input = True
  def _create_write(self, instruction):
    self.code.append("__write_at_{}_{}:".format(instruction.start_position, instruction.end_position))
    self._create_expression_evaluator(instruction.expression)
    self.code.append("\t\tpopq\t%rdi")
    self.code.append("\t\tcall\t__write_stdout")
    self.integer_output = True
  def _create_call(self, call):
    if call.procedure.instructions or call.procedure.return_type:
      if call.actuals:
        for actual in call.actuals.expressions:
          if type(actual.child) is ast.Location and actual.child.get_size() > 8:
            self._create_location_evaluator(actual.child)
          else:
            self._create_expression_evaluator(actual)
      self.code.append("\t\tcall\t__{}__".format(call.procedure.name))
      if not call.procedure.name in self.procedures:
        self.procedures[call.procedure.name] = call.procedure
      if call.procedure.formals:
        times = len(call.procedure.formals)
        self.code.append("\t\taddq\t${}, %rsp".format(times * integer_size))
  def _generate_instructions(self, instructions):
    for instruction in instructions:
      if type(instruction) is ast.Assign:
        self._create_assign(instruction)
      elif type(instruction) is ast.If:
        self._create_if(instruction)
      elif type(instruction) is ast.Repeat:
        self._create_repeat(instruction)
      elif type(instruction) is ast.Read:
        self._create_read(instruction)
      elif type(instruction) is ast.Call:
        self._create_call(instruction)
      else: # Write
        self._create_write(instruction)
  def _create_declarations(self):
    printed = False
    for name, type_object in self.table.scopes[1].symbols.iteritems():
      if not type(type_object) is symbol_table.Variable:
        continue
      if not printed:
        self.code.append("\n\t.data")
        printed = True
      self.code.append("{}_:\t\t.space {}".format(name, type_object.get_size()))
  def _link_library(self):
    zero_end = False
    error_integer_output = False
    write = False
    if self.div_zero:
      self.code.append(code_library.error_div_zero)
      declaration = "_div_error:\t\t.ascii \"error: The right side of the DIV expression at (\""
      self.read_only_declarations.append(declaration)
      zero_end = True
      error_integer_output = True
    if self.mod_zero:
      self.code.append(code_library.error_mod_zero)
      declaration = "_mod_error:\t\t.ascii \"error: The right size of the MOD expression at (\""
      self.read_only_declarations.append(declaration)
      zero_end = True
      error_integer_output = True
    if zero_end:
      declaration = "_zero_end:\t\t.ascii \") evaluated to zero\\n\""
      self.read_only_declarations.append(declaration)
    if self.index_range:
      self.code.append(code_library.error_index_range_code)
      declaration = "_index_range:\t.ascii \"error: Index out of range: the expression at (\""
      self.read_only_declarations.append(declaration)
      declaration = "_evaluated_to:\t.ascii \") evaluated to \""
      self.read_only_declarations.append(declaration)
      error_integer_output = True
    if self.integer_output:
      self.code.append(code_library.write_stdout_code)
      write = True
    if error_integer_output:
      self.code.append(code_library.write_stderr_code)
      write = True
    if write:
      self.code.append(code_library.write_code)
    if self.read_input:
      self.code.append(code_library.read_code)
      self.code.append(code_library.error_input)
      declaration = "_bad_input:\t\t.ascii \"error: The input was not an integer\\n\""
      self.read_only_declarations.append(declaration)
  def _create_procedure(self, procedure):
    self.code.append("__{}__:".format(procedure.name))
    self.code.append("\t\tpushq\t%rbp")
    self.code.append("\t\tmovq\t%rsp, %rbp")
    self.in_procedure = True
    self.formals = procedure.formals
    self.local_variables = procedure.local_variables
    if self.local_variables:
      offset = 0
      for var in self.local_variables.values():
        offset += var.get_size()
      times = offset / 8
      for i in range(times):
        self.code.append("\t\tpushq\t$0")
      self.code.append("\t\tpushq\t%rbx")
      self.code.append("\t\tleaq\t8(%rsp), %rbx")
    if procedure.instructions:
      self._generate_instructions(procedure.instructions.get_instructions())
    if procedure.return_expression:
      self._create_expression_evaluator(procedure.return_expression)
      self.code.append("\t\tpopq\t%rax")
    self.in_procedure = False
    if self.local_variables:
      self.code.append("\t\tmovq\t-8(%rbx), %rbx")
    self.code.append("\t\tmovq\t%rbp, %rsp")
    self.code.append("\t\tpopq\t%rbp")
    self.code.append("\t\tret")
  def generate(self):
    self.code = []
    self.read_only_declarations = []
    self.mod_zero = False
    self.div_zero = False
    self.index_range = False
    self.integer_output = False
    self.read_input = False
    self.node = 0
    self.procedures = {}
    self.in_procedure = False
    self.code.append("\t.globl\tmain\n")
    self.code.append("\t.text")
    self.code.append("main:\n")
    if self.tree:
      self._generate_instructions(self.tree.get_instructions())
    self.code.append("__end_program:")
    self.code.append("\t\tmovq\t$60, %rax")
    self.code.append("\t\tmovq\t$0, %rdi")
    self.code.append("\t\tsyscall\n")
    printed = []
    while self.procedures:
      old_procedures = self.procedures
      self.procedures = {}
      for procedure in old_procedures.values():
        if not procedure in printed:
          self._create_procedure(procedure)
          printed.append(procedure)
    if printed:
      self.code.append("")
    self._link_library()
    if self.table.scopes[1].symbols:
      self._create_declarations()
    if self.read_only_declarations:
      self.code.append("\n\t.section .rodata")
      for declaration in self.read_only_declarations:
        self.code.append(declaration)
    return self.code

