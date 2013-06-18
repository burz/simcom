import environment
import code_generator

class Symbol_table_exception(Exception):
  def __init__(self, error):
    self.error = error
  def __str__(self):
    return "error: " + self.error

class Entry(object):
  node = 0 # the next available node (graphical)
  base_types = {} # the base types already in the graph
  def __init__(self, start_position, end_position):
    self.start_position = start_position
    self.end_position = end_position
  def __str__(self):
    return "{}@({}, {})".format(type(self), self.start_position, self.end_position)

class Constant(Entry):
  def __init__(self, start_position, end_position, type_object, value):
    super(Constant, self).__init__(start_position, end_position)
    self.type_object = type_object
    self.value = value
  def print_string(self, current_level = 0, graphical = False):
    if not graphical:
      print "  " * current_level + "CONST BEGIN"
      print "  " * (current_level + 1) + "type:"
      self.type_object.print_string(current_level + 2, graphical)
      print "  " * (current_level + 1) + "value:"
      print "  " * (current_level + 2) + self.value.__str__()
      print "  " * current_level + "END CONST"
    else:   
      node = self.type_object.print_string(graphical = graphical)
      new_node = "node{}".format(Entry.node)
      Entry.node += 1
      print new_node, "[label=\"{}\",shape=diamond]".format(self.value)
      print new_node, "->", node
      return new_node

class Variable(Entry):
  def __init__(self, start_position, end_position, type_object):
    super(Variable, self).__init__(start_position, end_position)
    self.type_object = type_object
  def get_box(self):
    return self.type_object.get_box()
  def get_size(self):
    return self.type_object.get_size()
  def print_string(self, current_level = 0, graphical = False):
    if not graphical:
      print "  " * current_level + "VAR BEGIN"
      print "  " * (current_level + 1) + "type:"
      self.type_object.print_string(current_level + 2, graphical)
      print "  " * current_level + "END VAR"
    else:   
      node = self.type_object.print_string(graphical = graphical)
      new_node = "node{}".format(Entry.node)
      Entry.node += 1 
      print new_node, "[label=\"\",shape=circle]"
      print new_node, "->", node
      return new_node

class Integer(Entry):
  def __init__(self):
    self.printed = False
  def get_box(self):
    return environment.IntegerBox()
  def get_size(self):
    return code_generator.integer_size
  def print_string(self, current_level = 0, graphical = False):
    if not graphical:
      print "  " * current_level + "INTEGER"
    else:
      if self.printed:
        return self.printed
      new_node = "node{}".format(Entry.node)
      Entry.node += 1
      print new_node, "[label=\"Integer\",shape=box,style=rounded]"
      self.base_types[self] = new_node
      self.printed = new_node
      return new_node
  def __str__(self):
    return "INTEGER"

class Array(Entry):
  def __init__(self, start_position, end_position, element_type, length):
    super(Array, self).__init__(start_position, end_position)
    self.element_type = element_type
    self.length = length
    self.printed = False
  def get_box(self):
    return environment.ArrayBox(self.length, self.element_type.get_box())
  def get_size(self):
    return self.element_type.get_size() * self.length
  def get_offset(self):
    return self.element_type.get_size()
  def print_string(self, current_level = 0, graphical = False):
    if not graphical:
      print "  " * current_level + "ARRAY BEGIN"
      print "  " * (current_level + 1) + "type:"
      self.element_type.print_string(current_level + 2, graphical)
      print "  " * (current_level + 1) + "length:"
      print "  " * (current_level + 2) + self.length.__str__()
      print "  " * current_level + "END ARRAY"
    else:
      if self.printed:
        return self.printed
      node = self.element_type.print_string(graphical = graphical)
      new_node = "node{}".format(Entry.node)
      Entry.node += 1
      print new_node, "[label=\"Array\\nlength: {}\",shape=box,style=rounded]".format(self.length)
      print new_node, "->", node
      self.printed = new_node
      return new_node

class Record(Entry):
  def __init__(self, start_position, end_position, scope_object):
    super(Record, self).__init__(start_position, end_position)
    self.scope_object = scope_object
    self.printed = False
  def get_box(self):
    return environment.RecordBox(self.scope_object.create_environment())
  def get_size(self):
    size = 0
    for declaration in self.scope_object.symbols.values():
      size += declaration.get_size()
    return size
  def get_offset(self, name):
    offset = 0
    for key, value in self.scope_object.symbols.iteritems():
      if key == name:
        break
      offset += value.get_size()
    return offset
  def print_string(self, current_level = 0, graphical = False):
    if not graphical:
      print "  " * current_level + "RECORD BEGIN"
      self.scope_object.print_string(current_level + 1, graphical)
      print "  " * current_level + "END RECORD"
    else:
      if self.printed:
        return self.printed
      node = self.scope_object.print_string(graphical = graphical)
      new_node = "node{}".format(Entry.node)
      Entry.node += 1
      print new_node, "[label=\"Record\",shape=box,style=rounded]"
      print new_node, "->", node
      self.printed = new_node
      return new_node

def _compare_names(x, y): # Function for sorting names in Uppercase then letter order
  if len(x) < len(y):
    length = len(x)
    remember = -1
  else:
    length = len(y)
    remember = 1
  for i in range(length):
    if x[i] == y[i]:
      continue
    if x[i].isupper() and y[i].isupper():
      if x[i] < y[i]:
        return -1
      else:
        return 1
    if x[i].isupper() and not y[i].isupper():
      return -1
    elif not x[i].isupper() and y[i].isupper():
      return 1
    else:
      if x[i] < y[i]:
        return -1
      else:
        return 1
  if len(x) is len(y):
    return 0
  else:
    return remember

class Scope(object):
  cluster = 0 # the next available cluster number
  anchor = 0 # the next available anchor number
  def __init__(self, parent):
    self.symbols = {}
    self.parent = parent
  def insert(self, name, value):
    if name in self.symbols:
      return False
    else:
      self.symbols[name] = value
      return True
  def find(self, name):
    if not self.local(name):
      if not self.parent:
        return False
      return self.parent.find(name) # See if it is declared in the parent
    else:
      return self.symbols[name]
  def local(self, name):
    if name in self.symbols:
      return True
    else:
      return False
  def create_environment(self):
    boxes = {}
    for name in self.symbols:
      if not type(self.symbols[name]) is Variable:
        continue
      boxes[name] = self.symbols[name].get_box()
    return boxes
  def print_string(self, current_level = 0, graphical = False):
    if not graphical:
      print "  " * current_level + "SCOPE BEGIN"
      for key in sorted(self.symbols, _compare_names):
        print "  " * (current_level + 1) + key, "=>"
        self.symbols[key].print_string(current_level + 2, graphical)
      print "  " * current_level + "END SCOPE"
    else:
      scope_nodes = []
      scope_connections = []
      for key in sorted(self.symbols, _compare_names):
        node = self.symbols[key].print_string(graphical = graphical)
        new_node = "node{}".format(Entry.node)
        Entry.node += 1
        scope_nodes.append("{} [label=\"{}\",shape=box,color=white,fontcolor=black]".format(new_node, key))
        scope_connections.append(new_node + " -> " + node)
      cluster = "cluster{}".format(Scope.cluster)
      Scope.cluster += 1
      print "subgraph", cluster, "{"
      anchor = "anchor{}".format(Scope.anchor)
      Scope.anchor += 1
      print anchor, "[label=\"\",style=invis]"
      for node in scope_nodes:
        print node
      print "}"
      for connection in scope_connections:
        print connection
      return anchor

class Procedure(Entry):
  def __init__(self, start_position, end_position, name, formals, return_type, scope, instructions, return_expression):
    super(Procedure, self).__init__(start_position, end_position)
    self.name = name
    self.formals = formals
    self.return_type = return_type
    self.scope = scope
    removes = []
    if formals:
      for formal in formals:
        removes.append(formal[0].data)
    self.local_variables = {}
    for symbol, entry in scope.symbols.iteritems():
      if symbol in removes:
        continue
      self.local_variables[symbol] = entry
    self.instructions = instructions
    self.return_expression = return_expression
  def get_type(self):
    return self.return_type
  def print_string(self, current_level = 0, graphical = False):
    if not graphical:
      print "  " * current_level + "PROCEDURE BEGIN"
      if self.formals:
        print "  " * (current_level + 1) + "formals:"
        for formal in self.formals:
          print "  " * (current_level + 2), formal[0].data, "=>"
          formal[1].print_string(current_level + 3, graphical)
      print "  " * (current_level + 1) + "return type:"
      self.return_type.print_string(current_level + 2, graphical)
      print "  " * current_level + "PROCEDURE END"
    else:
      new_node = "node{}".format(Entry.node)
      Entry.node += 1
      print "{} [label=\"Procedure\",shape=triangle]".format(new_node)
      added_variables = []
      if self.formals:
        nodes = []
        for formal in self.formals:
          nodes.append(formal[1].print_string(graphical = graphical))
          added_variables.append(formal[0].data)
        print "subgraph cluster{}".format(Scope.cluster), "{"
        Scope.cluster += 1
        anchor = "anchor{}".format(Scope.anchor)
        Scope.anchor += 1
        print "{} [label=\"\",style=invis]".format(anchor)
        link = []
        for i, node in enumerate(nodes):
          label = "node{}".format(Entry.node)
          Entry.node += 1
          print "{} [label=\"{}\",shape=box,color=white,fontcolor=black]".format(label, self.formals[i][0].data)
          link.append(label)
        print "}"
        for i, link in enumerate(link):
          circle = "node{}".format(Entry.node)
          Entry.node += 1
          print circle, "[label=\"\",shape=circle]"
          print link, "->", circle
          print circle, "->", nodes[i]
        print new_node, "->", anchor, "[label=\"formals\"]"
      if self.scope.symbols:
        nodes = []
        for name, entry in self.scope.symbols.iteritems():
          if not name in added_variables:
            nodes.append((name, entry.print_string(graphical = graphical)))
        if nodes:
          print "subgraph cluster{}".format(Scope.cluster), "{"
          Scope.cluster += 1
          anchor = "anchor{}".format(Scope.anchor)
          Scope.anchor += 1
          print "{} [label=\"\",style=invis]".format(anchor)
          connections = []
          for node in nodes:
            label = "nodes{}".format(Entry.node)
            Entry.node += 1
            print label, "[label=\"{}\",shape=box,color=white,fontcolor=black]".format(node[0])
            connections.append((label, node[1]))
          print "}"
          for link in connections:
            print link[0], "->", link[1]
          print new_node, "->", anchor, "[label=\"scope\"]"
      if self.return_type:
        return_type = self.return_type.print_string(graphical = graphical)
        print new_node, "->", return_type, "[label=\"returns\"]"
      return new_node

class Symbol_table(object):
  integer = Integer() # Singleton Integer
  def __init__(self):
    universe = Scope(False)
    universe.insert("INTEGER", Symbol_table.integer)
    self.scopes = [universe] # A list of all the scopes in the symbol_table
    self.current_scope = [universe] # A stack with the current scope at the top
  def get_current_scope(self):
    return self.current_scope[len(self.current_scope) - 1]
  def push_scope(self):
    scope = Scope(self.get_current_scope())
    self.scopes.append(scope)
    self.current_scope.append(scope)
  def leave_scope(self):
    if len(self.current_scope) is 1:
      return False
    else:
      self.current_scope.pop()
      return True
  def get_int(self):
    return self.scopes[0].find("INTEGER")
  def get_environment(self):
    return self.scopes[1].create_environment()
  def print_table(self, graphical = False):
    program_scope = self.scopes[1]
    if graphical:
      print "Digraph X {"
    program_scope.print_string(graphical = graphical)
    if graphical:
      print "}"

