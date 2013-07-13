import environment
import lazy_generator

class Entry(object):
  node = -1
  anchor = -1
  cluster = -1
  def new_node(self):
    Entry.node += 1
    return "node_sym{}".format(Entry.node)
  def new_anchor(self):
    Entry.anchor += 1
    return "anchor_sym{}".format(Entry.anchor)
  def new_cluster(self):
    Entry.cluster += 1
    return "cluster_sym{}".format(Entry.cluster)

class Constant(Entry):
  def __init__(self, type_object, value, line):
    self.type_object = type_object
    self.value = value
    self.line = line
  def graphical(self):
    node = self.new_node()
    print node, "[label=\"{}\",shape=diamond]".format(self.value)
    print node + ' -> ' + self.type_object.graphical()
    return node

class Variable(Entry):
  def __init__(self, name, type_object, line):
    self.name = name
    self.type_object = type_object
    self.line = line
  def get_box(self):
    return type_object.get_box()
  def get_size(self):
    return type_object.get_size()
  def graphical(self):
    node = self.new_node()
    print node, '[label="",shape=circle]'
    print node + ' -> ' + self.type_object.graphical()
    return node

class Integer(Entry):
  def __init__(self):
    self.printed = False
  def get_box(self):
    return environment.IntegerBox()
  def get_size(self):
    return lazy_generator.INTEGER_SIZE
  def graphical(self):
    if self.printed:
      return self.printed
    node = self.new_node()
    print node, '[label="Integer",shape=box,style=rounded]'
    self.printed = node
    return node

class Array(Entry):
  def __init__(self, type_object, size, line):
    self.type_object = type_object
    self.size = size
    self.printed = False
  def get_box(self):
    return environment.ArrayBox(self.size, self.type_object.get_box())
  def get_size(self):
    return self.size * self.type_object.get_size()
  def graphical(self):
    if self.printed:
      return self.printed
    node = self.new_node()
    print node, "[label=\"Array\\nlength: {}".format(self.size) + '",shape=box,syle=rounded]'
    print node + ' -> '+ self.type_object.graphical()
    self.printed = node
    return node

class Record(Entry):
  def __init__(self, scope, line):
    self.scope = scope
    self.line = line
    self.printed = False
  def get_box(self):
    return environment.RecordBox(self.scope)
  def get_size(self):
    size = 0
    for type_object in self.scope.symbols.values():
      size += type_object.get_size()
    return size
  def graphical(self):
    if self.printed:
      return self.printed
    node = self.new_node()
    print node, '[label="Record",shape=box,style=rounded]'
    print node + ' -> ' + self.scope.graphical()
    self.printed = node
    return node

class Procedure(Entry):
  def __init__(self, name, formals, scope, type_object, instructions, return_expression, line):
    self.name = name
    self.formals = formals
    self.scope = scope
    self.type_object = type_object
    self.instructions = instructions
    self.return_expression = return_expression
    self.line = line
  def graphical(self):
    node = self.new_node()
    print node, '[label="' + self.name + '"]'
    if self.type_object:
      print node + ' -> ' + self.type_object.graphical(), '[label="returns"]'
    last_node = False
    if self.formals:
      for formal in self.formals:
        new_node = self.new_node()
        print new_node, '[label="' + formal + '",shape=circle]'
        if not last_node:
          print node, '->', new_node, '[label="formals"]'
        else:
          print last_node, '->', new_node
        last_node = new_node
    if self.scope.symbols:
      print node + ' -> ' + self.scope.graphical(), '[label="scope"]'
    return node

def compare_names(x, y):
  i = 0
  while len(x) > i and len(y) > i:
    if x[i] < y[i]:
      return -1
    elif x[i] > y[i]:
      return 1
    i += 1
  if len(x) is len(y):
    return 0
  if len(x) < len(y):
    return -1
  else:
    return 1

class Scope(object):
  node = -1
  anchor = -1
  cluster = -1
  def __init__(self, parent = False):
    self.symbols = {}
    self.parent = parent
  def new_node(self):
    Scope.node += 1
    return "node_scp{}".format(Scope.node)
  def new_anchor(self):
    Scope.anchor += 1
    return "anchor_scp{}".format(Scope.anchor)
  def new_cluster(self):
    Scope.cluster += 1
    return "cluster_scp{}".format(Scope.cluster)
  def insert(self, name, type_object):
    if name in self.symbols:
      return False
    self.symbols[name] = type_object
    return True
  def find(self, name):
    if not name in self.symbols.keys():
      if not self.parent:
        return False
      return self.parent.find(name)
    return self.symbols[name]
  def graphical(self):
    nodes = []
    connections = []
    for key in sorted(self.symbols, compare_names):
      node = self.new_node()
      nodes.append(node + ' [label="' + key + '",shape=box,color=white,fontcolor=black]')
      connections.append(node + ' -> ' + self.symbols[key].graphical())
    print 'subgraph', self.new_cluster(), '{'
    anchor = self.new_anchor()
    print anchor, '[label="",style=invis]'
    for node in nodes:
      print node
    print '}'
    for connection in connections:
      print connection
    return anchor

class Symbol_table(object):
  def __init__(self):
    self.integer_singleton = Integer()
    universal_scope = Scope(False)
    universal_scope.insert('INTEGER', self.integer_singleton)
    self.scopes = [universal_scope]
    self.scopes.append(Scope(universal_scope))
  def find(self, name):
    return self.scopes[-1].find(name)
  def insert(self, name, type_object):
    return self.scopes[-1].insert(name, type_object)
  def current_scope(self):
    return self.scopes[-1]
  def push_scope(self):
    self.scopes.append(Scope(self.scopes[-1]))
  def pop_scope(self):
    return self.scopes.pop()
  def graphical(self):
    print 'Digraph X {'
    self.scopes[1].graphical()
    print '}'

