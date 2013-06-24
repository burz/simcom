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
  def __init__(self, instructions, line):
    self.instructions = instructions
    self.line = line
  def graphical(self):
    first_node = self.instructions[0].graphical()
    last_node = first_node
    for instruction in instructions[1:]:
      new_node = instruction.graphical()
      print "{rank=same;", last_node, "->", new_node, "[label=\"next\"]}"
    return first_node

class Instruction(Node):
  def __init__(self, child, line):
    self.child = child
    self.line = line
  def graphical(self):
    return self.child.graphical()

class Assign(Node):
  def __init__(self, location, expression, line):
    self.location = location
    self.expression = expression
    self.line = line
  def graphical(self):
    node = self.new_node()
    print node, '[label=":=",shape=rectangle]'
    location = self.location.graphical()
    print node, '->', location, '[label="location"]'
    expression = self.expression.graphical()
    print node, '->', expression, '[label="expression"]'
    return node

class If(Node):
  def __init__(self, condition, instructions_true, instructions_false, line):
    self.condition = condition
    self.instructions_true = instructions_true
    self.instructions_false = instructions_false
    self.line = line
  def graphical(self):
    node = self.new_node()
    print node, '[label="If",shape=rectangle]'
    condition = self.condition.graphical()
    print node, '->', condition, '[label="condition"]'
    instructions_true = self.instructions_true.graphical()
    print node, '->', instructions_true, '[label="true"]'
    if self.instructions_false:
      instructions_false = self.instructions_false.graphical()
      print node, '->', instructions_false, '[label="false"]'
    return node

class Repeat(Node):
  def __init__(self, condition, instructions, line):
    self.condition = condition
    self.instructions = instructions
    self.line = line
  def graphical(self):
    node = self.new_node()
    print node, '[label="Repeat",shape=rectangle]'
    condition = self.condition.graphical()
    print node, '->', condition, '[label="condition"]'
    instructions = self.instructions.graphical()
    print node, '->', instructions, '[label="instructions"]'
    return node

class Read(Node):
  def __init__(self, location, line):
    self.location = location
    self.line = line

class Write(Node):
  def __init__(self, expression, line):
    self.expression = expression
    self.line = line

class Location(Node):
  def __init__(self, child, type_object, line):
    self.child = child
    self.type_object = type_object
    self.line = line

class Expression(Node):
  def __init__(self, child, type_object, line):
    self.child = child
    self.type_object = type_object
    self.line = line

class Condition(Node):
  def __init__(self, relation, expression_left, expression_right, line):
    self.relation = relation
    self.expression_left = expression_left
    self.expression_right = expression_right
    self.line = line

class Variable(Node):
  def __init__(self, name, table_entry, line):
    self.name = name
    self.table_entry = table_entry
    self.line = line

class Index(Node):
  def __init__(self, location, expression, type_object, line):
    self.location = location
    self.expression = expression
    self.table_entry = type_object
    self.line = line

class Field(Node):
  def __init__(self, location, variable, type_object, line):
    self.location = location
    self.variable = variable
    self.table_entry = type_object
    self.line = line

class Number(Node):
  def __init__(self, table_entry, line):
    self.table_entry = table_entry
    self.line = line

class Binary(Node):
  def __init__(self, operator, expression_left, expression_right, line):
    self.operator = operator
    self.expression_left = expression_left
    self.expression_right = expression_right
    self.line = line

class Call(Node):
  def __init__(self, definition, actual_expressions, type_object, line):
    self.definition = definition
    self.actual_expressions = actual_expressions
    self.table_entry = type_object
    self.line = line

class Syntax_tree(object):
  def __init__(self, instructions):
    self.instructions = instructions

