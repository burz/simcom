class Entry(object):
  node = -1
  anchor = -1
  cluster = -1
  def new_node(self):
    Entry.node += 1
    return "symbol_node{}".format(Entry.node)
  def new_anchor(self):
    Entry.anchor += 1
    return "symbol_anchor{}".format(Entry.anchor)
  def new_cluster(self):
    Entry.cluster += 1
    return "symbol_cluster{}".format(Entry.cluster)

class Constant(Entry):
  def __init__(self, type_object, value, line):
    self.type_object = type_object
    self.value = value
    self.line = line

class Variable(Entry):
  def __init__(self, name, type_object, line):
    self.name = name
    self.type_object = type_object
    self.line = line

class Integer(Entry):
  pass

class Array(Entry):
  def __init__(self, type_object, size, line):
    self.type_object = type_object
    self.size = size

class Record(Entry):
  def __init__(self, scope, line):
    self.scope = scope
    self.line = line

class Procedure(Entry):
  def __init__(self, name, formals, type_object, instructions, return_expression, line):
    self.name = name
    self.formals = formals
    self.type_object = type_object
    self.instructions = instructions
    self.return_expression = return_expression
    self.line = line

class Scope(object):
  anchor = -1
  cluster = -1
  def __init__(self, parent = False):
    self.symbols = {}
    self.parent = parent
  def new_anchor(self):
    Scope.anchor += 1
    return "scope_anchor{}".format(Scope.anchor)
  def new_cluster(self):
    Scope.cluster += 1
    return "scope_cluster{}".format(Scope.cluster)
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

class Symbol_table(object):
  def __init__(self):
    self.integer_singleton = Integer()
    universal_scope = Scope(False)
    universal_scope.insert('INTEGER', self.integer_singleton)
    self.scopes = [universal_scope]
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

