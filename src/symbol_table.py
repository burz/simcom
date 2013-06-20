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
  def __init__(self, type_object, value, line_number):
    self.type_object = type_object
    self.value = value
    self.line_number = line_number

class Variable(Entry):
  def __init__(self, name, type_object, line_number):
    self.name = name
    self.type_object = type_object
    self.line_number = line_number

class Integer(Entry):
  pass

class Array(Entry):
  def __init__(self, type_object, size, line_number):
    self.type_object = type_object
    self.size = size

class Record(Entry):
  def __init__(self, scope, line_number):
    self.scope = scope
    self.line_number = line_number

class Procedure(Entry):
  pass

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
  integer_singleton = Integer()
  def __init__(self):
    universal_scope = Scope(False)
    universe.insert('Integer', Symbol_table.integer_singleton)
    self.scopes = [universal_scope]
  def current_scope(self):
    return self.scopes[-1]
  def push_scope(self):
    self.scopes.append(Scope(self.scopes[-1]))
  def pop_scope(self):
    return self.scopes.pop()

