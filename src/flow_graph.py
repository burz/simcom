import intermediate_code_generator

class Block(object):
  handle = -1
  def __init__(self):
    self.lines = []
    self.parents = []
    self.next_block = False
    self.jump_block = False
    self.printed = False
  def new_node(self):
    Block.handle += 1
    return "node_block_{}".format(Block.handle)
  def add_line(self, line):
    self.lines.append(line)
  def add_parent(self, parent):
    self.parents.appent(parent)
  def set_next_block(self, next_block):
    self.next_block = next_block
  def set_jump_block(self, jump_block):
    self.jump_block = jump_block
  def is_end(self):
    return not self.lines
  def graphical(self):
    if self.printed:
      return self.printed
    node = self.new_node()
    content = self.lines[0].__repr__()
    for line in self.lines[1:]:
      content += '\\n' + line.__repr__()
    print node, '[label="' + content + '",shape=rectangle]'
    if self.next_block and not self.next_block.is_end():
      print node + ' -> ' + self.next_block.graphical(), '[label="next"]'
    if self.jump_block and not self.jump_block.is_end():
      print node + ' -> ' + self.jump_block.graphical(), '[label="jump"]'
    self.printed = node
    return node

class Flow_graph(object):
  def __init__(self, intermediate_code):
    self.intermediate_code = intermediate_code
    self.labeled_blocks = {}
    self.generate_blocks()
  def line(self):
    if self.position >= len(self.intermediate_code) or self.position < 0:
      return False
    return self.intermediate_code[self.position]
  def next_line(self):
    self.position += 1
  def previous_line(self):
    self.position -= 1
  def generate_blocks(self):
    self.position = 0
    self.start = Block()
    current_block = self.start
    while self.line():
      line = self.line()
      if type(line) in [intermediate_code_generator.Unconditional_jump,
                        intermediate_code_generator.Conditional_jump]:
        current_block.add_line(line)
        if not line.line in self.labeled_blocks:
          self.labeled_blocks[line.line] = Block()
        label_block = self.labeled_blocks[line.line]
        current_block.set_jump_block(label_block)
        label_block.add_parent(current_block)
        old_block = current_block
        current_block = Block()
        old_block.set_next_block(current_block)
      elif type(line) is intermediate_code_generator.Label:
        old_block = current_block
        if not line.line in self.labeled_blocks:
          self.labeled_blocks[line.line] = Block()
        current_block = self.labeled_blocks[line.line]
        old_block.set_next_block(current_block)
      elif type(line) in [intermediate_code_generator.Call,
                          intermediate_code_generator.Division,
                          intermediate_code_generator.Write,
                          intermediate_code_generator.Read]:
        current_block.add_line(line)
        old_block = current_block
        current_block = Block()
        old_block.set_next_block(current_block)
      else:
        current_block.add_line(line)
      self.next_line()
  def graphical(self):
    print 'strict digraph X {'
    self.start.graphical()
    print '}'

