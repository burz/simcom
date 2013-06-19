class Node(object):
  node = -1
  anchor = -1
  cluster = -1
  def new_node(self):
    Node.node += 1
    return Node.node
  def new_anchor(self):
    Node.anchor += 1
    return Node.anchor
  def new_cluster(self):
    Node.cluster += 1
    return Node.cluster

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
  def __init__(self, relation, expression_right, expression_left, line_number):
    self.relation = relation
    self.expression_right = expression_right
    self.expression_left = expression_left
    self.line_number = line_number

class Variable(Node):
class Index(Node):
class Field(Node):
class Number(Node):
class Binary(Node):

