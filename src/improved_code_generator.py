# Anthony Burzillo
# aburzil1@jhu.edu
#
# improved_code_generator.py

import ast
import optimize
import pool

from code_generator import Code_generator, integer_size

def log_2(power_of_two):
  """Determines the base 2 logarithm of a number that is a power of two

  power_of_two := a number x where x = 2**i for some i >= 0

  Returns the logarithm

  """
  power = 0
  while not power_of_two is 1:
    power += 1
    power_of_two = power_of_two >> 1
  return power

class Improved_code_generator(Code_generator):
  def __init__(self, table, tree):
    """Create a code generator

    table: the symbol table for the code
    tree: the abstract syntax tree for the code

    """
    self.table = table
    self.tree = tree
    self.registers = pool.Pool()
  def _replace_register_placeholder(self, register, code, label = "#@@"):
    new_code = []
    for line in code:
      new_code.append(line.replace(label, register))
    return new_code
  def _check_priority(self, used_one, used_two, order = False):
    result = False
    if self.registers.caller:
      for register in self.registers.caller:
        if not register in used_one:
          if not order:
            result = -1
            break
        if not register in used_two:
          result = 1
          break
    if not result:
      return False
    return result, register
  def _decide_priority(self, one_used, one_code, two_used, two_code, register, order = False):
    code = []
    result = self._check_priority(one_used, two_used, order)
    if result:
      if result[0] is 1:
        code += self._replace_register_placeholder(register, two_code)
        return result[0], result[1], code
      else:
        code += self._replace_register_placeholder(register, one_code)
        return result[0], result[1], code
    two = self.registers.get_callee(code)
    code += self._replace_register_placeholder(register, one_code) + self._replace_register_placeholder(two, two_code)
    return result, register, two, code
  def _decide_expression_priority(self, expression, right_used, right_code, left_used, left_code, register, order = False):
    if type(expression) is ast.Expression:
      node = expression.child
    else:
      node = expression
    code = []
    results = self._decide_priority(left_used, left_code, right_used, right_code, register, order)
    if not results[0]:
      one = register
      two = results[2]
      code += results[3] 
    elif results[0] is 1:
      one = register
      two = self.registers.request_register(results[1], code)
      right_used, right_code = self._create_expression_evaluator(node.expression_right, two)
      code += right_code + results[2]
    else:
      two = register
      one = self.registers.request_register(results[1], code)
      left_used, left_code = self._create_expression_evaluator(node.expression_left, one)
      code += left_code + results[2]
    used_registers = right_used + left_used + [one, two]
    return one, two, used_registers, code
  def _create_location_evaluator(self, location, register = "#@@"): # Generate code to evaluate a location
    offset, used_registers, code = self.__create_location_evaluator(location, register)
    if offset:
      code.append("\t\taddq\t${}, {}".format(offset, register))
      return offset, used_registers, code
    else:
      return "", used_registers, code
  def __create_location_evaluator(self, location, register): # Helper function to evaluate a location
    used_registers = []
    if type(location.child) is ast.Field:
      offset_sum, used, code = self.__create_location_evaluator(location.child.location, register)
      used_registers += used
      if type(location.child.location.child) is ast.Field:
        offset = location.child.location.child.variable.table_entry.type_object.get_offset(location.child.variable.name)
      elif type(location.child.location.child) is ast.Index:
        offset = location.child.location.child.table_entry.get_offset(location.child.variable.name)
      else: # Variable
        offset = location.child.location.child.table_entry.type_object.get_offset(location.child.variable.name)
      return offset_sum + offset, used_registers, code
    elif type(location.child) is ast.Index:
      offset_sum, used, code = self.__create_location_evaluator(location.child.location, register)
      used_registers += used
      if not type(location.child.expression.child) is ast.Number:
        if offset_sum:
          code.append("\t\taddq\t${}, {}".format(offset_sum, register))
        temp = self.registers.get_caller()
        used_registers.append(temp)
        used, expression_code = self._create_expression_evaluator(location.child.expression, temp)
        code += expression_code
        used_registers += used
        code.append("\t\tcmpq\t$0, {}".format(temp))
        code.append("\t\tjl\t\t_error{}_".format(self.node))
        code.append("\t\tcmpq\t${}, {}".format(location.child.table_entry.length, temp))
        code.append("\t\tjl\t\t_no_error{}_".format(self.node))
        code.append("_error{}_:".format(self.node))
        code.append("\t\tmovq\t${}, %rdi".format(location.child.expression.start_position))
        code.append("\t\tmovq\t${}, %rsi".format(location.child.expression.end_position))
        code.append("\t\tmovq\t{}, %rdx".format(temp))
        code.append("\t\tjmp\t\t__error_index_range")
        code.append("_no_error{}_:".format(self.node))
        offset = location.child.table_entry.get_offset()
        if offset & (offset) - 1 is 0:
          code.append("\t\tsalq\t${}, {}".format(log_2(offset), temp))
        else:
          code.append("\t\timulq\t${}, {}".format(offset, temp))
        code.append("\t\taddq\t{}, {}".format(temp, register))
        self.registers.return_registers(1, code)
        self.node += 1
        self.index_range = True
        return 0, used_registers, code
      else:
        offset = location.child.table_entry.get_offset() * location.child.expression.child.table_entry.value
        return offset_sum + offset, used_registers, code
    else: # Variable
      code = []
      if not self.in_procedure:
        code.append("\t\tmovq\t${}_, {}".format(location.child.name, register))
      else:
        if location.child.name in self.local_variables:
          offset = 8
          for name, var in self.local_variables.iteritems():
            if name == location.child.name:
              break
            offset += var.get_size()
          code.append("\t\tleaq\t-{}(%rbp), {}".format(offset, register))
          return 0, used_registers, code
        offset = -1
        n = 0
        if self.formals:
          for formal in self.formals:
            if formal[0].data == location.child.name:
                offset = 8 * (n + 2)
            n += 1
        if not offset is -1:
          if not location.get_size() is integer_size:
            code.append("\t\tmovq\t{}(%rbp), {}".format(offset, register))
          else:
            code.append("\t\tleaq\t{}(%rbp), {}".format(offset, register))
        else:
          code.append("\t\tmovq\t${}_, {}".format(location.child.name, register))
      return 0, used_registers, code
  def _create_expression_evaluator(self, expression, register = "#@@"): # Generate code to evaluate an expression
    used_registers = []
    code = []
    if type(expression.child) is ast.Number:
      code.append("\t\tmovq\t${}, {}".format(expression.child.table_entry.value, register))
    elif type(expression.child) is ast.Location:
      if self.in_procedure and type(expression.child.child) is ast.Variable and self.formals:
        n = 2
        for formal in self.formals:
          if expression.child.child.name == formal[0].data:
            code.append("\t\tleaq\t{}(%rbp), {}".format(n * 8, register))
          n += 1
      else:
        offset, used, code = self._create_location_evaluator(expression.child, register)
        if offset:
          code.pop()
        used_registers += used
        code.append("\t\tmovq\t{0}({1}), {1}".format(offset, register))
    elif type(expression.child) is ast.Binary:
      left_used, left_code = self._create_expression_evaluator(expression.child.expression_left)
      right_used, right_code = self._create_expression_evaluator(expression.child.expression_right)
      if expression.child.operator.data == "+":
        if not type(expression.child.expression_right.child) is ast.Number:
          if not type(expression.child.expression_left.child) is ast.Number:
            one, two, used_registers, code = self._decide_expression_priority(expression, left_used, left_code, right_used, right_code, register)
            if one == register:
              code.append("\t\taddq\t{}, {}".format(two, one))
            else:
              code.append("\t\taddq\t{}, {}".format(one, two))
            self.registers.return_registers(1, code)
          else:
            value = expression.child.expression_left.child.table_entry.value
            code += self._replace_register_placeholder(register, right_code)
            used_registers = right_used
            code.append("\t\taddq\t${}, {}".format(value, register))
        else:
          value = expression.child.expression_right.child.table_entry.value
          code += self._replace_register_placeholder(register, left_code)
          used_registers = left_used
          code.append("\t\taddq\t${}, {}".format(value, register))
      elif expression.child.operator.data == "-":
        if not type(expression.child.expression_right.child) is ast.Number:
          one, two, used_registers, code = self._decide_expression_priority(expression, left_used, left_code, right_used, right_code, register, True)
          code.append("\t\tsubq\t{}, {}".format(two, one))
          self.registers.return_registers(1, code)
        else:
          value = expression.child.expression_right.child.table_entry.value
          code += self._replace_register_placeholder(register, left_code)
          used_registers = left_used
          code.append("\t\tsubq\t${}, {}".format(value, register))
      elif expression.child.operator.data == "*":
        if not type(expression.child.expression_right.child) is ast.Number:
          if not type(expression.child.expression_left.child) is ast.Number:
            one, two, used_registers, code = self._decide_expression_priority(expression, left_used, left_code, right_used, right_code, register)
            if one == register:
              code.append("\t\timulq\t{}, {}".format(two, one))
            else:
              code.append("\t\timulq\t{}, {}".format(one, two))
            self.registers.return_registers(1, code)
          else:
            value = expression.child.expression_left.child.table_entry.value
            code += self._replace_register_placeholder(register, right_code)
            used_registers = right_used
            if value & (value - 1) is 0:
              code.append("\t\tsalq\t${}, {}".format(log_2(value), register))
            else:
              code.append("\t\timulq\t${}, {}".format(value, register))
        else:
          value = expression.child.expression_right.child.table_entry.value
          code += self._replace_register_placeholder(register, left_code)
          used_registers = left_used
          if value & (value - 1) is 0:
            code.append("\t\tsalq\t${}, {}".format(log_2(value), register))
          else:
            code.append("\t\timulq\t${}, {}".format(value, register))
      else:
        self.registers.request_register("%rax", code)
        left_used, left_code = self._create_expression_evaluator(expression.child.expression_left)
        right_used, right_code = self._create_expression_evaluator(expression.child.expression_right)
        one, two, used_registers, code = self._decide_expression_priority(expression, left_used, left_code, right_used, right_code, "%rax", True)
        if expression.child.operator.data == "DIV":
          if not type(expression.child.expression_right.child) is ast.Number:
            code.append("\t\tcmpq\t$0, {}".format(two))
            code.append("\t\tjne\t\t_no_error{}_".format(self.node))
            code.append("\t\tmovq\t${}, %rdi".format(expression.start_position))
            code.append("\t\tmovq\t${}, %rsi".format(expression.end_position))
            code.append("\t\tjmp\t\t__error_div_zero")
            code.append("_no_error{}_:".format(self.node))
            self.node += 1
            self.div_zero = True
          code.append("\t\tmovq\t%rax, %rdx")
          code.append("\t\tsarq\t$63, %rdx")
          code.append("\t\tidivq\t{}".format(two))
          if not register == "%rax":
            code.append("\t\tmovq\t%rax, {}".format(register))
        else: # MOD
          if not type(expression.child.expression_right.child) is ast.Number:
            code.append("\t\tcmpq\t$0, {}".format(two))
            code.append("\t\tjne\t\t_no_error{}_".format(self.node))
            code.append("\t\tmovq\t${}, %rdi".format(expression.start_position))
            code.append("\t\tmovq\t${}, %rsi".format(expression.end_position))
            code.append("\t\tjmp\t\t__error_mod_zero")
            code.append("_no_error{}_:".format(self.node))
            self.node += 1
            self.mod_zero = True
          code.append("\t\tmovq\t%rax, %rdx")
          code.append("\t\tsarq\t$63, %rdx")
          code.append("\t\tidivq\t{}".format(two))
          if not register == "%rdx":
            code.append("\t\tmovq\t%rdx, {}".format(register))
        self.registers.return_registers(1, code)
        used_registers += ["%rax", "%rdx"]
    elif type(expression.child) is ast.Call:
      used_registers, call_code = self._create_call(expression.child)
      code += call_code
      if not register == "%rax":
        code.append("\t\tmovq\t%rax, {}".format(register))
    return used_registers, code
  def _create_condition_evaluator(self, condition): # Generate code to evaluate a condition
    code = []
    register = self.registers.get_caller()
    left_used, left_code = self._create_expression_evaluator(condition.expression_left)
    right_used, right_code = self._create_expression_evaluator(condition.expression_right)
    if not type(condition.expression_right.child) is ast.Number:
        one, two, used_registers, code = self._decide_expression_priority(condition, left_used, left_code, right_used, right_code, register)
        code.append("\t\tcmpq\t{}, {}".format(two, one))
        self.registers.return_registers(2, code)
        used_registers += [one, two]
    else:
      code += self._replace_register_placeholder(register, left_code)
      used_registers = left_used
      code.append("\t\tcmpq\t${}, {}".format(condition.expression_right.child.table_entry.value, register))
      self.registers.return_registers(1, code)
      used_registers.append(register)
    if condition.relation.data == "=":
      code.append("\t\tje\t\t_true{}_".format(self.node))
      code.append("\t\tjmp\t\t_false{}_".format(self.node))
    elif condition.relation.data == "#":
      code.append("\t\tjne\t\t_true{}_".format(self.node))
      code.append("\t\tjmp\t\t_false{}_".format(self.node))
    elif condition.relation.data == "<":
      code.append("\t\tjl\t\t_true{}_".format(self.node))
      code.append("\t\tjmp\t\t_false{}_".format(self.node))
    elif condition.relation.data == ">":
      code.append("\t\tjg\t\t_true{}_".format(self.node))
      code.append("\t\tjmp\t\t_false{}_".format(self.node))
    elif condition.relation.data == "<=":
      code.append("\t\tjle\t\t_true{}_".format(self.node))
      code.append("\t\tjmp\t\t_false{}_".format(self.node))
    else: # >=
      code.append("\t\tjge\t\t_true{}_".format(self.node))
      code.append("\t\tjmp\t\t_false{}_".format(self.node))
    return used_registers, code
  def _create_assign(self, instruction): # Generate code to run an assign instruction
    code = ["__assign_at_{}_{}:".format(instruction.start_position, instruction.end_position)]
    used_registers = []
    if type(instruction.expression.child) is ast.Number:
      location_offset, location_used, location_code = self._create_location_evaluator(instruction.location)
      if location_offset:
        location_code.pop()
      destination = self.registers.get_unused(location_used)
      used_registers += location_used + [destination]
      code += self._replace_register_placeholder(destination, location_code)
      code.append("\t\tmovq\t${}, {}({})".format(instruction.expression.child.table_entry.value, location_offset, destination))
      self.registers.return_registers(1, code)
    else:
      count = instruction.location.get_size() / integer_size
      register = self.registers.get_caller()
      location_offset, location_used, location_code = self._create_location_evaluator(instruction.location)
      if location_offset:
        location_code.pop()
      used_registers += location_used
      expression_offset = ""
      if count is 1:
        expression_used, expression_code = self._create_expression_evaluator(instruction.expression)
      else:
        expression_offset, expression_used, expression_code = self._create_location_evaluator(instruction.expression.child)
        if expression_offset:
          expression_code.pop()
      used_registers += expression_used
      results = self._decide_priority(location_used, location_code, expression_used, expression_code, register)
      if not results[0]:
        destination = register
        source = results[2]
        code += results[3] 
      elif results[0] is 1:
        source = register
        destination = self.registers.request_register(results[1], code)
        location_offset, location_used, location_code = self._create_location_evaluator(instruction.location, destination)
        if location_offset:
          location_code.pop()
        code += location_code + results[2]
      else:
        destination = register
        source = self.registers.request_register(results[1], code)
        if count is 1:
          expression_used, expression_code = self._create_expression_evaluator(instruction.expression, source)
        else:
          expression_offset, expression_used, expression_code = self._create_location_evaluator(instruction.expression.child, source)
          if expression_offset:
            expression_code.pop()
        code += expression_code + results[2]
      used_registers += location_used + expression_used + [destination, source]
      if count > 1:
        temp1 = self.registers.get_caller()
        temp2 = self.registers.get_caller()
        used_registers += [temp1, temp2]
        code.append("\t\tmovq\t${}, {}".format(count, temp1))
        code.append("_loop{}_:".format(self.node))
        code.append("\t\tmovq\t{}({}), {}".format(expression_offset, source, temp2))
        code.append("\t\tmovq\t{}, {}({})".format(temp2, location_offset, destination))
        code.append("\t\taddq\t$8, {}".format(source))
        code.append("\t\taddq\t$8, {}".format(destination))
        code.append("\t\tdecq\t{}".format(temp1))
        code.append("\t\tjnz\t\t_loop{}_".format(self.node))
        self.node += 1
        self.registers.return_registers(4, code)
      else:
        code.append("\t\tmovq\t{}, {}({})".format(source, location_offset, destination))
        self.registers.return_registers(2, code)
    return used_registers, code
  def _create_if(self, instruction): # Generate code to run an if instruction
    code = ["__if_at_{}_{}:".format(instruction.start_position, instruction.end_position)]
    used_registers, condition_code = self._create_condition_evaluator(instruction.condition)
    code += condition_code
    code.append("_true{}_:".format(self.node))
    node_number = self.node
    self.node += 1
    used, instruction_code = self._generate_instructions(instruction.instructions_true.get_instructions())
    used_registers += used
    code += instruction_code
    if instruction.instructions_false:
      code.append("\t\tjmp\t\t_end{}_".format(node_number))
    code.append("_false{}_:".format(node_number))
    if instruction.instructions_false:
      used, instruction_code = self._generate_instructions(instruction.instructions_false.get_instructions())
      used_registers += used
      code += instruction_code
      code.append("_end{}_:".format(node_number))
    return used_registers, code
  def _create_repeat(self, instruction): # Generate code to run a repeat instruction
    label = "__repeat_at_{}_{}".format(instruction.start_position, instruction.end_position)
    code = [label + ":"]
    used_registers, condition_code = self._create_condition_evaluator(instruction.condition)
    code += condition_code
    code.append("_false{}_:".format(self.node))
    node_number = self.node
    self.node += 1
    used, instruction_code = self._generate_instructions(instruction.instructions.get_instructions())
    used_registers += used
    code += instruction_code
    code.append("\t\tjmp\t\t{}".format(label))
    code.append("_true{}_:".format(node_number))
    return used_registers, code
  def _create_read(self, instruction): # Generate code to run a read instruction
    code = ["__read_at_{}_{}:".format(instruction.start_position, instruction.end_position)]
    destination = self.registers.get_callee(code)
    offset, used, location_code = self._create_location_evaluator(instruction.location, destination)
    code += location_code
    code.append("\t\tcall\t__read")
    code.append("\t\tmovq\t%rax, {}({})".format(offset, destination))
    self.registers.return_registers(1, code)
    self.read_input = True
    return pool.caller, code
  def _create_write(self, instruction): # Generate code to run a write instruction
    code = ["__write_at_{}_{}:".format(instruction.start_position, instruction.end_position)]
    self.registers.request_register("%rdi", code)
    used, expression_code = self._create_expression_evaluator(instruction.expression, "%rdi")
    code += expression_code
    code.append("\t\tcall\t__write_stdout")
    self.integer_output = True
    self.registers.return_registers(1, code)
    return pool.caller, code
  def _create_call(self, call):
    code = ["__call_at_{}_{}:".format(call.start_position, call.end_position)]
    used_registers = []
    if not call.procedure.instructions and call.procedure.return_expression and type(call.procedure.return_expression.child) is ast.Number:
      code.append("\t\tmovq\t${}, %rax".format(call.procedure.return_expression.child.table_entry.value))
    elif call.procedure.instructions or call.procedure.return_type:
      argument_size = 0
      if call.actuals:
        argument_size = len(call.actuals.expressions) * 8
        if argument_size > 0:
          code.append("\t\tsubq\t${}, %rsp".format(argument_size))
        for i, actual in enumerate(call.actuals.expressions):
          temp = self.registers.get_caller()
          used_registers.append(temp)
          offset = (i + 2) * 8
          used, expression_code = self._create_expression_evaluator(actual, temp)
          used_registers += used
          code += expression_code
          code.append("\t\tmovq\t{}, {}(%rsp)".format(temp, offset))
      code.append("\t\tcall\t__{}__".format(call.procedure.name))
      if not call.procedure.name in self.procedures:
        self.procedures[call.procedure.name] = call.procedure
      if call.actuals:
        self.registers.return_registers(i, code)
      if argument_size > 0:
        code.append("\t\taddq\t${}, %rsp".format(argument_size))
    return used_registers, code
  def _create_procedure(self, procedure):
    code = ["__{}__:".format(procedure.name)]
    code.append("\t\tpushq\t%rbp")
    code.append("\t\tmovq\t%rsp, %rbp")
    self.in_procedure = True
    self.formals = procedure.formals
    self.local_variables = procedure.local_variables
    used_registers = []
    if self.local_variables:
      offset = 0
      for var in self.local_variables.values():
        offset += var.get_size()
      code.append("\t\tsubq\t${}, %rsp".format(offset))
      times = offset / 8
      for i in range(times):
        if not i:
          code.append("\t\tmovq\t$0, (%rsp)")
          continue
        code.append("\t\tmovq\t$0, {}(%rsp)".format(i * 8))
    self.registers.enter_procedure(procedure)
    if procedure.instructions:
      used, instruction_code = self._generate_instructions(procedure.instructions.get_instructions())
      used_registers += used
      code += instruction_code
    if procedure.return_expression:
      self.registers.request_register("%rax", code)
      used, return_code = self._create_expression_evaluator(procedure.return_expression, "%rax")
      used_registers += used
      code += return_code
      used_registers.append("%rax")
      self.registers.return_registers(1, code)
    self.in_procedure = False
    code.append("\t\tmovq\t%rbp, %rsp")
    code.append("\t\tpopq\t%rbp")
    code.append("\t\tret")
    return used_registers, code
  def _generate_instruction(self, instruction):
    if type(instruction) is ast.Assign:
      used, code = self._create_assign(instruction)
    elif type(instruction) is ast.If:
      used, code = self._create_if(instruction)
    elif type(instruction) is ast.Repeat:
      used, code = self._create_repeat(instruction)
    elif type(instruction) is ast.Read:
      used, code = self._create_read(instruction)
    elif type(instruction) is ast.Call:
      used, code = self._create_call(instruction)
    else: # Write
      used, code = self._create_write(instruction)
    return used, code
  def _generate_instructions(self, instructions): # Generate code to run a set of instructions
    used_registers = []
    instruction_code = []
#   print "START", self.registers.caller
    for instruction in instructions:
      used, code = self._generate_instruction(instruction)
      used_registers += used
      instruction_code += code
#   print "END  ", self.registers.caller
    return used_registers, instruction_code
  def generate(self):
    """Generate the code for a program

    Returns a list containing the code

    """
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
      used, code = self._generate_instructions(self.tree.get_instructions())
      self.code += code
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
          used, code = self._create_procedure(procedure)
          self.code += code
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
    self.code = optimize.consolidate_multiple_labels(self.code)
#   self.code = optimize.delete_unused_labels(self.code)
    return self.code

