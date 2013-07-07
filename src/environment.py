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

class RecordBox(object):
  def __init__(self, scope):
    if not scope:
      self.fields = Environment.make_environment(scope)
  def copy(self):
    new_fields = {}
    for field in self.fields:
      new_fields[field] = self.fields[field].copy()
    new = RecordBox()
    new.fields = new_fields
    return new
  def set_to(self, record):
    self.fields = record.copy().fields
  def get_box(self, name):
    return self.fields[name]

class Environment(object):
  def __init__(self, scope):
    self.boxes = make_environment(scope)
  def make_environment(scope):
    fields = {}
    for symbol in scope.symbols:
      fields[symbol] = symbols[symbol].get_box()
    return fields
  def get_box(self, name):
    return self.boxes[name]

