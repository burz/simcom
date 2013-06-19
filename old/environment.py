import ast

class IntegerBox(object):
  def __init__(self):
    self.value = 0
  def copy(self):
    new_box = IntegerBox()
    new_box.value = self.value
    return new_box
  def set_value(self, value):
    self.value = value
  def get_value(self):
    return self.value

class ArrayBox(object):
  def __init__(self, size, type_instance = False):
    self.size = size
    self.boxes = []
    if type_instance:
      for i in range(size):
        self.boxes.append(type_instance.copy())
  def copy(self):
    new_box = ArrayBox(self.size)
    for box in self.boxes:
      new_box.boxes.append(box.copy())
    return new_box
  def set_to(self, box):
    self.boxes = box.copy().boxes
  def get_box(self, index):
    if index >= self.size:
      return False
    return self.boxes[index]

class RecordBox(object):
  def __init__(self, fields):
    self.fields = fields
  def copy(self):
    fields = {}
    for field in self.fields:
      fields[field] = self.fields[field].copy()
    return RecordBox(fields)
  def set_to(self, box):
    self.fields = box.copy().fields
  def get_box(self, name):
    if not name in self.fields:
      return False
    return self.fields[name]

class Environment(object):
  def __init__(self, table = False):
    if table:
      self.boxes = table.get_environment()
    else:
      self.boxes = False
  def get_box(self, name):
    if not name in self.boxes:
      return False
    return self.boxes[name]

