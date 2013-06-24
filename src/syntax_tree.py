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
  def graphical(self):
    node = self.new_node()
    print node, '[label="Read",shape=rectangle]'
    location = self.location.graphical()
    print node, '->', location, '[label="location"]'
    return node

class Write(Node):
  def __init__(self, expression, line):
    self.expression = expression
    self.line = line
  def graphical(self):
    node = self.new_node()
    print node, '[label="Write",shape=rectangle]'
    expression = self.expression.graphical()
    print node, '->', expression, '[label="expression"]'
    return node

class Location(Node):
  def __init__(self, child, type_object, line):
    self.child = child
    self.type_object = type_object
    self.line = line
  def graphical(self):
    return self.child.graphical()

class Expression(Node):
  def __init__(self, child, type_object, line):
    self.child = child
    self.type_object = type_object
    self.line = line
  def graphical(self):
    return self.child.graphical()

class Condition(Node):
  def __init__(self, relation, expression_left, expression_right, line):
    self.relation = relation
    self.expression_left = expression_left
    self.expression_right = expression_right
    self.line = line
  def graphical(self):
    node = self.new_node()
    print node, '[label="' + self.operator + '",shape=rectangle]'
    left = self.expression_left.graphical()
    print node, '->', left, '[label="left"]'
    right = self.expression_right.graphical()
    print node, '->', right, '[label="right"]'
    return node

class Variable(Node):
  def __init__(self, name, table_entry, line):
    self.name = name
    self.table_entry = table_entry
    self.line = line
  def graphical(self):
    node = self.new_node()
    print node, '[label="Variable",shape=rectangle]'
    variable = self.new_node()
    print variable, '[label="' + self.name + '",shape=circle]'
    print node, '->', variable, '[label="ST"]'
    return node

class Index(Node):
  def __init__(self, location, expression, type_object, line):
    self.location = location
    self.expression = expression
    self.table_entry = type_object
    self.line = line
  def graphical(self):
    node = self.new_node()
    print node, '[label="Index",shape=rectangle]'
    location = self.location.graphical()
    print node, '->', location, '[label="location"]'
    expression = self.expression.graphical()
    print node, '->', expression, '[label="expression"]'
    return node

class Field(Node):
  def __init__(self, location, variable, type_object, line):
    self.location = location
    self.variable = variable
    self.table_entry = type_object
    self.line = line
  def graphical(self):
    node = self.new_node()
    print node, '[label="Field",shape=rectangle]'
    location = self.location.graphical()
    print node, '->', location, '[label="location"]'
    variable = self.variable.graphical()
    print node, '->', variable, '[label="variable"]'
    return node

class Number(Node):
  def __init__(self, table_entry, line):
    self.table_entry = table_entry
    self.line = line
  def graphical(self):
    node = self.new_node()
    print node, '[label="Number",shape=rectangle]'
    value = self.new_node()
    print value, "[label=\"{}\",shape=diamond]".format(self.table_entry.value)
    print node, '->', value, '[label="ST"]'
    return node

class Binary(Node):
  def __init__(self, operator, expression_left, expression_right, line):
    self.operator = operator
    self.expression_left = expression_left
    self.expression_right = expression_right
    self.line = line
  def graphical(self):
    node = self.new_node()
    print node, '[label="' + self.operator + '",shape=rectangle]'
    left = self.expression_left.graphical()
    print node, '->', left, '[label="left"]'
    right = self.expression_right.graphical()
    print node, '->', right, '[label="right"]'
    return node

class Call(Node):
  def __init__(self, definition, actuals, type_object, line):
    self.definition = definition
    self.actuals = actuals
    self.table_entry = type_object
    self.line = line
  def graphical(self):
    node = self.new_node()
    print node, '[label="Call",shape=rectangle]'
    procedure = self.new_node()
    print procedure, '[label="' + self.definition.name + '"]'
    print node, '->', procedure, '[label="procedure"]'
    if self.actuals:
      cluster = self.new_cluster()
      print 'subgraph', cluster, '{'
      new_nodes = []
      for actual in actuals:
        expression = actual.graphical()
        new_nodes.append(expression)
      print '}'
      for i, formal in enumerate(self.definition.formals):
        print node, '->', new_nodes[i], '[label="' + formal + '"]'
      return node

class Syntax_tree(object):
  def __init__(self, instructions):
    self.instructions = instructions

