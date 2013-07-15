class Block(object):
  def __init__(self, lines):
    self.lines = lines
    self.parents = []
    self.children = []
  def add_parent(self, parent):
    self.parents.appent(parent)
  def add_child(self, child):
    self.children.append(child)
  def set_next_block(self, next_block):
    self.next_block = next_block

class Flow_graph(object):
  def __init__(self, intermediate_code):
    self.head = head
    self.end = end
