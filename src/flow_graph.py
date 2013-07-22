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
    self.parents.append(parent)
  def set_next_block(self, next_block):
    self.next_block = next_block
  def set_jump_block(self, jump_block):
    self.jump_block = jump_block
  def is_end(self):
    return not self.lines and not self.next_block
  def graphical(self):
    if self.printed:
      return self.printed
    if not self.lines:
      if not self.next_block:
        node = self.new_node()
        print node, '[label="END",shape=diamond]'
        self.printed = node
        return node
      else:
        node = self.next_block.graphical()
        self.printed = node
        return node
    node = self.new_node()
    content = ""
    for line in self.lines:
      if type(line) in [intermediate_code_generator.Unconditional_jump,
                        intermediate_code_generator.Conditional_jump]:
        string = '\\n' + line.__repr__(False)
      else:
        string = '\\n' + line.__repr__()
      content += string
    print node, '[label="' + content[2:] + '",shape=rectangle]'
    self.printed = node
    if self.next_block:
      print node + ' -> ' + self.next_block.graphical(), '[label="next"]'
    if self.jump_block:
      print node + ' -> ' + self.jump_block.graphical(), '[label="jump"]'
    return node

class Flow_graph(object):
  node = -1
  end_singleton = Block()
  def __init__(self, intermediate_code):
    self.intermediate_code = intermediate_code
    self.labeled_blocks = {}
    self.generate_blocks()
    self.attach_liveness()
  def new_node(self):
    Flow_graph.node += 1
    return "node_flow_{}".format(Flow_graph.node)
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
        current_block.add_parent(old_block)
      elif type(line) is intermediate_code_generator.Label:
        old_block = current_block
        if not line in self.labeled_blocks:
          self.labeled_blocks[line] = Block()
        current_block = self.labeled_blocks[line]
        old_block.set_next_block(current_block)
        current_block.add_parent(old_block)
      elif type(line) in [intermediate_code_generator.Call,
                          intermediate_code_generator.Division,
                          intermediate_code_generator.Write,
                          intermediate_code_generator.Read]:
        current_block.add_line(line)
        old_block = current_block
        current_block = Block()
        old_block.set_next_block(current_block)
        current_block.add_parent(old_block)
      else:
        current_block.add_line(line)
      self.next_line()
  def attach_liveness(self):
    blocks = []
    current_block = self.start
    while not current_block.is_end():
      blocks[:0] = [current_block]
      current_block = current_block.next_block
    self.live = {}
    for block in blocks[::-1]:
      block.live_on_exit = []  
      for location in self.live:
        if self.live[location]:
          block.live_on_exit.append(self.live[location])
      for line in block.lines[::-1]:
        if type(line) is intermediate_code_generator.Assign:
          line.location_live = self.lookup_status(line.location_value)
          line.expression_live = self.lookup_status(line.expression_value)
          self.set_status(line.location_value, False)
          self.set_status(line.expression_value, True)
        elif type(line) in [intermediate_code_generator.Binary,
                            intermediate_code_generator.Division,
                            intermediate_code_generator.Compare]:
          line.left_live = self.lookup_status(line.left_value)
          line.right_live = self.lookup_status(line.right_value)
          self.set_status(line.left_value, True)
          self.set_status(line.right_value, True)
        elif type(line) in [intermediate_code_generator.Call,
                            intermediate_code_generator.Read]:
          for location in self.live:
            self.set_status(location, False)
        elif type(line) is intermediate_code_generator.Write:
          line.value_live = self.lookup_status(line.value)
          for location in self.live:
            self.set_status(location, False)
          self.set_status(line.value, True)
      block.live_on_entry = []  
      for location in self.live:
        if self.live[location]:
          block.live_on_entry.append(self.live[location])
  def set_status(self, location, live):
    if not location[0] == '$':
      self.live[location] = live
  def lookup_status(self, location):
    if not location in self.live:
      return False
    return self.live[location]
  def graphical(self):
    print 'digraph X {'
    start = self.new_node()
    print start, '[label="START",shape=diamond]'
    print start + ' -> ' + self.start.graphical()
    print '}'

