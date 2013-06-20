class Node(object):
  node = -1
  anchor = -1
  cluster = -1
  def new_node(self):
    Node.node += 1
    return "syntax_node{}".format(Node.node)
  def new_anchor(self):
    Node.anchor += 1
    return "syntax_anchor{}".format(Node.anchor)
  def new_cluster(self):
    Node.cluster += 1
    return "syntax_cluster{}".format(Node.cluster)

class Instructions(Node):
  def __init__(self, instructions, line_number):
    self.instructions = instructions
    self.line_number = line_number

class Instruction(Node):
  def __init__(self, child, line_number):
    self.child = child
    self.line_number = line_number

class Assign(Node):
  def __init__(self, location, expression, line_number):
    self.location = location
    self.expression = expression
    self.line_number = line_number

class If(Node):
  def __init__(self, condition, instructions_true, instructions_false, line_number):
    self.condition = condition
    self.instructions_true = instructions_true
    self.instructions_false = instructions_false
    self.line_number = line_number

class Repeat(Node):
  def __init__(self, condition, instructions, line_number):
    self.condition = condition
    self.instructions = instructions
    self.line_number = line_number

class Read(Node):
  def __init__(self, location, line_number):
    self.location = location
    self.line_number = line_number

class Write(Node):
  def __init__(self, expression, line_number):
    self.expression = expression
    self.line_number = line_number

class Location(Node):
  def __init__(self, child, line_number):
    self.child = child
    self.line_number = line_number

class Expression(Node):
  def __init__(self, child, line_number):
    self.child = child
    self.line_number = line_number

class Condition(Node):
  def __init__(self, relation, expression_left, expression_right, line_number):
    self.relation = relation
    self.expression_left = expression_left
    self.expression_right = expression_right
    self.line_number = line_number

class Variable(Node):
  def __init__(self, name, table_entry, line_number):
    self.name = name
    self.table_entry = table_entry
    self.line_number = line_number

class Index(Node):
  def __init__(self, location, expression, table_entry, line_number):
    self.location = location
    self.expression = expression
    self.table_entry = table_entry
    self.line_number = line_number

class Field(Node):
  def __init__(self, location, variable, table_entry, line_number):
    self.location = location
    self.variable = variable
    self.table_entry = table_entry
    self.line_number = line_number

class Number(Node):
  def __init__(self, table_entry, line_number):
    self.table_entry = table_entry
    self.line_number = line_number

class Binary(Node):
  def __init__(self, operator, expression_left, expression_right, line_number):
    self.operator = operator
    self.expression_left = expression_left
    self.expression_right = expression_right
    self.line_number = line_number

class Call(Node):
  def __init__(self, table_entry, actual_expressions, line_number):
    self.table_entry = table_entry
    self.actual_expressions = actual_expressions
    self.line_number = line_number

class Syntax_tree(object):
  def __init__(self, instructions):
    self.instructions = instructions

