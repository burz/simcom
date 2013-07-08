import symbol_table

class IntegerBox(object):
  def __init__(self, value = False):
    if value:
      self.value = value
    else:
      self.value = 0
  def copy(self):
    return IntegerBox(self.value)
  def set_to(self, integer):
    self.value = integer.value

class ArrayBox(object):
  def __init__(self, size, instance):
    self.size = size
    self.boxes = []
    if instance:
      for i in range(size):
        self.boxes.append(instance.copy())
  def copy(self):
    new = ArrayBox(self.size, False)
    for box in self.boxes:
      new.boxes.append(box.copy)
    return new
  def set_to(self, array):
    for this, other in zip(self.boxes, array.boxes):
      this.set_to(other.copy())
  def get_box(self, index):
    if index >= self.size:
      return False
    return self.boxes[index]

class RecordBox(object):
  def __init__(self, scope):
    if scope:
      self.fields = make_environment(scope)
    else:
      self.fields = {}
  def copy(self):
    new_fields = {}
    for field in self.fields:
      new_fields[field] = self.fields[field].copy()
    new = RecordBox(False)
    new.fields = new_fields
    return new
  def set_to(self, record):
    self.fields = record.copy().fields
  def get_box(self, name):
    return self.fields[name]

def make_environment(scope):
  fields = {}
  for symbol in scope.symbols:
    if type(scope.symbols[symbol]) is symbol_table.Variable:
      fields[symbol] = scope.symbols[symbol].get_box()
  return fields

class Environment(object):
  def __init__(self, scope):
    self.boxes = make_environment(scope)
  def get_box(self, name):
    return self.boxes[name]

