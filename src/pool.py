caller = ["%rax", "%r10", "%r11", "%rdi", "%rsi", "%rdx", "%rcx", "%r8", "%r9"]
callee = ["%rbx", "%r12", "%r13", "%r14", "%r15"]

class Pool_exception(Exception):
  def __init__(self, error):
    self.error = error
  def __str__(self):
    return "error: {}".format(error)

class Pool(object):
  def __init__(self):
    self.caller = caller
    self.callee = callee
    self.stack = []
    self.stacks = {}
    for register in caller + callee:
      self.stacks[register] = 0
    self.last_picked = []
  def enter_procedure(self, procedure):
    self.stack.append(self.caller)
  def exit_procedure(self):
    self.caller = self.stack.pop()
  def get_unused(self, used):
    unused = False
    for register in self.caller:
      if not register in used:
        self.caller.remove(register)
        self.last_picked.append(register)
        unused = register
        break
    if not unused:
      unused = self.get_callee()
    return unused
  def get_caller(self):
    if not self.caller:
      raise Pool_exception("Ran out")
    register = self.caller.pop()
    self.last_picked.append(register)
    return register
  def get_callee(self, code):
    if not self.callee:
      raise Pool_exception("Ran out")
    register = self.callee.pop()
    code.append("\t\tpushq\t{}".format(register))
    self.last_picked.append(register)
    return register
  def request_register(self, register, code):
    if not register in self.caller:
      self.stacks[register] += 1
      code.append("\t\tpushq\t{}".format(register))
    else:
      self.caller.remove(register)
    self.last_picked.append(register)
    return register
  def return_registers(self, number, code):
    for i in range(number):
      register = self.last_picked.pop()
      if self.stacks[register]:
        self.stacks[register] -= 1
        code.append("\t\tpopq\t{}".format(register))
      elif register in callee:
        self.callee.append(register)
        code.append("\t\tpopq\t{}".format(register))
      else:
        self.caller.append(register)

