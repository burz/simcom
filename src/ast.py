# Anthony Burzillo
# aburzil1@jhu.edu
#
# ast.py

import symbol_table

class AST_exception(Exception):
	def __init__(self, error):
		self.error = error
	def __str__(self):
		return "error: {}".format(self.error)

class Node(object):
	node = 0 # The next available node number
	def __init__(self, start_position, end_position):
		"""Create a node

		start_position := the starting position of the node
		end_position := the ending position of the node

		"""
		self.start_position = start_position
		self.end_position = end_position
	def __str__(self):
		return "{}@({}, {})".format(type(self), self.start_position, self.end_position)

class Instructions(Node):
	def __init__(self, start_position, end_position, instructions):
		"""Create a node

		start_position := the starting position of the node
		end_position := the ending position of the node
		instructions := a list of the instruction nodes in the program

		"""
		super(Instructions, self).__init__(start_position, end_position)
		self.instructions = instructions
	def get_instructions(self):
		"""Get the instructions

		Returns a list containing the instructions

		"""
		return self.instructions
	def executes_call(self):
		for instruction in self.instructions:
			if instruction.executes_call():
				return True
		return False
	def print_string(self, current_level = 0, graphical = False):
		"""Print out a string representing the node

		current_level := the level of the node in the tree
		graphical := True if a graphical representation should be printed

		Returns the top node label if graphical is True

		"""
		if not graphical:
			for instruction in self.instructions:
				instruction.print_string(current_level, graphical)
		else:
			first_node = False
			last_node = False
			for instruction in self.instructions:
				node = instruction.print_string(graphical = graphical)
				if not first_node:
					first_node = node
				if last_node:
					print "{rank=same;", last_node, "->", node, "[label=\"next\"];}"
				last_node = node
			return first_node

class Assign(Node):
	def __init__(self, start_position, end_position, location, expression):
		"""Create a node

		start_position := the starting position of the node
		end_position := the ending position of the node
		location := the location to assign to
		expression := the value to assign

		"""
		super(Assign, self).__init__(start_position, end_position) 
		self.location = location
		self.expression = expression
	def executes_call(self):
		if self.location.executes_call() or self.expression.executes_call():
			return True
		return False
	def print_string(self, current_level = 0, graphical = False):
		"""Print out a string representing the node

		current_level := the level of the node in the tree
		graphical := True if a graphical representation should be printed

		Returns the top node label if graphical is True

		"""
		if not graphical:
			print "  " * current_level + "Assign:"
			print "  " * current_level + "location =>"
			self.location.print_string(current_level + 1, graphical)
			print "  " * current_level + "expression =>"
			self.expression.print_string(current_level + 1, graphical)
		else:
			new_node = "node{}".format(Node.node)
			Node.node += 1
			print new_node, "[label=\":=\",shape=rectangle]"
			location = self.location.print_string(graphical = graphical)
			print new_node, "->", location, "[label=\"location\"]"
			expression = self.expression.print_string(graphical = graphical)
			print new_node, "->", expression, "[label=\"expression\"]"
			return new_node

class Symbol(Node):
	def __init__(self, start_position, end_position, table_entry):
		"""Create a node

		start_position := the starting position of the node
		end_position := the ending position of the node
		table_entry := the table entry of the symbol

		"""
		super(Symbol, self).__init__(start_position, end_position)
		self.table_entry = table_entry

class Variable(Symbol):
	def __init__(self, start_position, end_position, name, table_entry):
		"""Create a node

		start_position := the starting position of the node
		end_position := the ending position of the node
		name := the name of the variable
		table_entry := the table entry of the variable

		"""
		super(Variable, self).__init__(start_position, end_position, table_entry)
		self.name = name
	def get_type(self):
		"""Get the type object of the node

		Returns the type object of the node

		"""
		return self.table_entry.type_object
	def get_size(self):
		"""Get in bytes the size of the variable

		Returns the size

		"""
		return self.table_entry.get_size()
	def executes_call(self):
		return False
	def print_string(self, current_level = 0, graphical = False):
		"""Print out a string representing the node

		current_level := the level of the node in the tree
		graphical := True if a graphical representation should be printed

		Returns the top node label if graphical is True

		"""
		if not graphical:
			print "  " * current_level + "Variable:"
			print "  " * current_level + "variable =>"
			self.table_entry.print_string(current_level + 1, graphical)
		else:
			new_node = "node{}".format(Node.node)
			Node.node += 1
			print new_node, "[label=\"{}\",shape=circle]".format(self.name)
			parent_node = "node{}".format(Node.node)
			Node.node += 1
			print parent_node, "[label=\"Variable\",shape=rectangle]"
			print parent_node, "->", new_node, "[label=\"ST\"]"
			return parent_node

class Index(Symbol):
	def __init__(self, start_position, end_position, location, expression, table_entry):
		"""Create a node

		start_position := the starting position of the node
		end_position := the ending position of the node
		location := the object to be indexed
		expression := the index
		table_entry := the table entry of the symbol

		"""
		super(Index, self).__init__(start_position, end_position, table_entry)
		self.location = location
		self.expression = expression
	def get_type(self):
		"""Get the type object of the node

		Returns the type object of the node

		"""
		return self.table_entry.element_type
	def get_size(self):
		"""Get the size in bytes of the space accessed by the index

		Returns the size

		"""
		return self.table_entry.get_offset()
	def executes_call(self):
		if self.location.executes_call() or self.expression.executes_call():
			return True
		return False
	def print_string(self, current_level = 0, graphical = False):
		"""Print out a string representing the node

		current_level := the level of the node in the tree
		graphical := True if a graphical representation should be printed

		Returns the top node label if graphical is True

		"""
		if not graphical:
			print "  " * current_level + "Index:"
			print "  " * current_level + "location =>"
			self.location.print_string(current_level + 1, graphical)
			print "  " * current_level + "expression =>"
			self.expression.print_string(current_level + 1, graphical)
		else:
			new_node = "node{}".format(Node.node)
			Node.node += 1
			print new_node, "[label=\"Index\",shape=rectangle]"
			location = self.location.print_string(graphical = graphical)
			print new_node, "->", location, "[label=\"location\"]"
			expression = self.expression.print_string(graphical = graphical)
			print new_node, "->", expression, "[label=\"expression\"]"
			return new_node

class Field(Node):
	def __init__(self, start_position, end_position, location, variable):
		"""Create a node

		start_position := the starting position of the node
		end_position := the ending position of the node
		location := the record
		variable := the field

		"""
		super(Field, self).__init__(start_position, end_position)
		self.location = location
		self.variable = variable
	def get_type(self):
		"""Get the type object of the node

		Returns the type object of the node

		"""
		return self.variable.get_type()
	def get_size(self):
		"""Gets the size in bytes of the location referenced by the field

		Returns the size

		"""
		return self.variable.get_size()
	def executes_call(self):
		return self.location.executes_call()
	def print_string(self, current_level = 0, graphical = False):
		"""Print out a string representing the node

		current_level := the level of the node in the tree
		graphical := True if a graphical representation should be printed

		Returns the top node label if graphical is True

		"""
		if not graphical:
			print "  " * current_level + "Field:"
			print "  " * current_level + "location =>"
			self.location.print_string(current_level + 1, graphical)
			print "  " * current_level + "variable =>"
			self.variable.print_string(current_level + 1, graphical)
		else:
			new_node = "node{}".format(Node.node)
			Node.node += 1
			print new_node, "[label=\"Field\",shape=rectangle]"
			location = self.location.print_string(graphical = graphical)
			print new_node, "->", location, "[label=\"location\"]"
			variable = self.variable.print_string(graphical = graphical)
			print new_node, "->", variable, "[label=\"variable\"]"
			return new_node

class Read(Node):
	def __init__(self, start_position, end_position, location):
		"""Create a node

		start_position := the starting position of the node
		end_position := the ending position of the node

		"""
		super(Read, self).__init__(start_position, end_position)
		self.location = location
	def executes_call(self):
		return self.location.executes_call()
	def print_string(self, current_level = 0, graphical = False):
		"""Print out a string representing the node

		current_level := the level of the node in the tree
		graphical := True if a graphical representation should be printed

		Returns the top node label if graphical is True

		"""
		if not graphical:
			print "  " * current_level + "Read:"
			print "  " * current_level + "location =>"
			self.location.print_string(current_level + 1, graphical)
		else:
			new_node = "node{}".format(Node.node)
			Node.node += 1
			print new_node, "[label=\"Read\",shape=rectangle]"
			location = self.location.print_string(graphical = graphical)
			print new_node, "->", location, "[label=\"location\"]"
			return new_node

class If(Node):
	def __init__(self, start_position, end_position, condition, instructions_true, instructions_false):
		"""Create a node

		start_position := the starting position of the node
		end_position := the ending position of the node
		condition := the condition of the if statement
		instructons_true := the instructions to be executed if true
		instructions_false := the instructions to be executed if false

		"""
		super(If, self).__init__(start_position, end_position)
		self.condition = condition
		self.instructions_true = instructions_true
		self.instructions_false = instructions_false
	def executes_call(self):
		if self.condition.executes_call() or self.instructions_true.executes_call():
			return True
		if self.instructions_false and self.instructions_false.executes_call():
			return True
		return False
	def print_string(self, current_level = 0, graphical = False):
		"""Print out a string representing the node

		current_level := the level of the node in the tree
		graphical := True if a graphical representation should be printed

		Returns the top node label if graphical is True

		"""
		if not graphical:
			print "  " * current_level + "If:"
			print "  " * current_level + "condition =>"
			self.condition.print_string(current_level + 1, graphical)
			print "  " * current_level + "true =>"
			self.instructions_true.print_string(current_level + 1, graphical)
			if self.instructions_false:
				print "  " * current_level + "false =>"
				self.instructions_false.print_string(current_level + 1, graphical)
		else:
			new_node = "node{}".format(Node.node)
			Node.node += 1
			print new_node, "[label=\"If\",shape=rectangle]"
			condition = self.condition.print_string(graphical = graphical)
			print new_node, "->", condition, "[label=\"condition\"]"
			true = self.instructions_true.print_string(graphical = graphical)
			print new_node, "->", true, "[label=\"true\"]"
			if self.instructions_false:
				false = self.instructions_false.print_string(graphical = graphical)
				print new_node, "->", false, "[label=\"false\"]"
			return new_node

class Repeat(Node):
	def __init__(self, start_position, end_position, condition, instructions):
		"""Create a node

		start_position := the starting position of the node
		end_position := the ending position of the node
		condition := the condition to repeat until
		instructions := the instructions to repeat

		"""
		super(Repeat, self).__init__(start_position, end_position)
		self.condition = condition
		self.instructions = instructions
	def executes_call(self):
		return self.condition.executes_call() or self.instructions.executes_call()
	def print_string(self, current_level = 0, graphical = False):
		"""Print out a string representing the node

		current_level := the level of the node in the tree
		graphical := True if a graphical representation should be printed

		Returns the top node label if graphical is True

		"""
		if not graphical:
			print "  " * current_level + "Repeat:"
			print "  " * current_level + "condition =>"
			self.condition.print_string(current_level + 1, graphical)
			print "  " * current_level + "instructions =>"
			self.instructions.print_string(current_level + 1, graphical)
		else:
			new_node = "node{}".format(Node.node)
			Node.node += 1
			print new_node, "[label=\"Repeat\",shape=rectangle]"
			condition = self.condition.print_string(graphical = graphical)
			print new_node, "->", condition, "[label=\"condition\"]"
			instructions = self.instructions.print_string(graphical = graphical)
			print new_node, "->", instructions, "[label=\"instructions\"]"
			return new_node

class Write(Node):
	def __init__(self, start_position, end_position, expression):
		"""Create a node

		start_position := the starting position of the node
		end_position := the ending position of the node
		expression := the expression to write

		"""
		super(Write, self).__init__(start_position, end_position)
		self.expression = expression
	def executes_call(self):
		return expression.executes_call()
	def print_string(self, current_level = 0, graphical = False):
		"""Print out a string representing the node

		current_level := the level of the node in the tree
		graphical := True if a graphical representation should be printed

		Returns the top node label if graphical is True

		"""
		if not graphical:
			print "  " * current_level + "Write:"
			print "  " * current_level + "expression =>"
			self.expression.print_string(current_level + 1, graphical)
		else:
			new_node = "node{}".format(Node.node)
			Node.node += 1
			print new_node, "[label=\"Write\",shape=rectangle]"
			expression = self.expression.print_string(graphical = graphical)
			print new_node, "->", expression, "[label=\"expression\"]"
			return new_node

class Expression(Node):
	def __init__(self, start_position, end_position, child):
		"""Create a node

		start_position := the starting position of the node
		end_position := the ending position of the node
		child := the child of the expression

		"""
		super(Expression, self).__init__(start_position, end_position)
		self.child = child
	def get_type(self):
		"""Get the type object of the node

		Returns the type object of the node

		"""
		return self.child.get_type()
	def executes_call(self):
		return self.child.executes_call()
	def print_string(self, current_level = 0, graphical = False):
		"""Print out a string representing the node

		current_level := the level of the node in the tree
		graphical := True if a graphical representation should be printed

		Returns the top node label if graphical is True

		"""
		if not graphical:
			self.child.print_string(current_level, graphical)
		else:
			return self.child.print_string(graphical = graphical)

class Number(Symbol):
	def __init__(self, start_position, end_position, table_entry):
		"""Create a node

		start_position := the starting position of the node
		end_position := the ending position of the node
		table_entry := the table entry of the number

		"""
		super(Number, self).__init__(start_position, end_position, table_entry)
	def get_type(self):
		"""Get the type object of the node

		Returns the type object of the node

		"""
		return symbol_table.Symbol_table.integer
	def executes_call(self):
		return False
	def print_string(self, current_level = 0, graphical = False):
		"""Print out a string representing the node

		current_level := the level of the node in the tree
		graphical := True if a graphical representation should be printed

		Returns the top node label if graphical is True

		"""
		if not graphical:
			print "  " * current_level + "Number:"
			print "  " * current_level + "value =>"
			self.table_entry.print_string(current_level + 1, False)
		else:
			new_node = "node{}".format(Node.node)
			Node.node += 1
			print new_node, "[label=\"{}\",shape=diamond]".format(self.table_entry.value)
			parent_node = "node{}".format(Node.node)
			Node.node += 1
			print parent_node, "[label=\"Number\",shape=rectangle]"
			print parent_node, "->", new_node, "[label=\"ST\"]"
			return parent_node


class Location(Node):
	def __init__(self, start_position, end_position, child):
		"""Create a node

		start_position := the starting position of the node
		end_position := the ending position of the node
		child := the child of the location

		"""
		super(Location, self).__init__(start_position, end_position)
		self.child = child
	def get_type(self):
		"""Get the type object of the node

		Returns the type object of the node

		"""
		return self.child.get_type()
	def get_size(self):
		"""Get in bytes the size of the location

		Returns the size

		"""
		return self.child.get_size()
	def execute_call(self):
		return self.child.executes_call()
	def print_string(self, current_level = 0, graphical = False):
		"""Print out a string representing the node

		current_level := the level of the node in the tree
		graphical := True if a graphical representation should be printed

		Returns the top node label if graphical is True

		"""
		if not graphical:
			self.child.print_string(current_level, graphical)
		else:
			return self.child.print_string(graphical = graphical)

class Binary(Node):
	def __init__(self, start_position, end_position, operator, expression_left, expression_right):
		"""Create a node

		start_position := the starting position of the node
		end_position := the ending position of the node
		operator := the operator of the binary node
		expression_left := the left side of the binary expression
		expression_right := the right side of the binary expression 

		"""
		super(Binary, self).__init__(start_position, end_position)
		self.operator = operator
		self.expression_left = expression_left
		self.expression_right = expression_right
	def get_type(self):
		"""Get the type object of the node

		Returns the type object of the node

		"""
		return symbol_table.Symbol_table.integer
	def executes_call(self):
		return self.expression_left.executes_call() or self.expression_right.executes_call()
	def print_string(self, current_level = 0, graphical = False):
		"""Print out a string representing the node

		current_level := the level of the node in the tree
		graphical := True if a graphical representation should be printed

		Returns the top node label if graphical is True

		"""
		if not graphical:
			print "  " * current_level + "Binary ({}):".format(self.operator.data)
			print "  " * current_level + "left =>"
			self.expression_left.print_string(current_level + 1, graphical)
			print "  " * current_level + "right =>"
			self.expression_right.print_string(current_level + 1, graphical)
		else:
			new_node = "node{}".format(Node.node)
			Node.node += 1
			print new_node, "[label=\"{}\",shape=rectangle]".format(self.operator.data)
			left = self.expression_left.print_string(graphical = graphical)
			print new_node, "->", left, "[label=\"left\"]"
			right = self.expression_right.print_string(graphical = graphical)
			print new_node, "->", right, "[label=\"right\"]"
			return new_node

class Condition(Node):
	def __init__(self, start_position, end_position, relation, expression_left, expression_right):
		"""Create a node

		start_position := the starting position of the node
		end_position := the ending position of the node
		relation := the relation of the expression
		expression_left := the left side of the conditional expression
		expression_right := the right side of the conditional expression

		"""
		super(Condition, self).__init__(start_position, end_position)
		self.relation = relation
		self.expression_left = expression_left
		self.expression_right = expression_right
	def executes_call(self):
		return self.expression_left.executes_call() or self.expression_right.executes_call()
	def print_string(self, current_level = 0, graphical = False):
		"""Print out a string representing the node

		current_level := the level of the node in the tree
		graphical := True if a graphical representation should be printed

		Returns the top node label if graphical is True

		"""
		if not graphical:
			print "  " * current_level + "Condition ({}):".format(self.relation.data)
			print "  " * current_level + "left =>"
			self.expression_left.print_string(current_level + 1, graphical)
			print "  " * current_level + "right =>"
			self.expression_right.print_string(current_level + 1, graphical)
		else:
			new_node = "node{}".format(Node.node)
			Node.node += 1
			print new_node, "[label=\"{}\",shape=rectangle]".format(self.relation.data)
			left = self.expression_left.print_string(graphical = graphical)
			print new_node, "->", left, "[label=\"left\"]"
			right = self.expression_right.print_string(graphical = graphical)
			print new_node, "->", right, "[label=\"right\"]"
			return new_node

class Actuals(Node):
	def __init__(self, start_position, end_position, expressions):
		"""Create a node

		start_position := the starting position of the node
		end_position := the ending position of the node
		expressions := a list of the expressions

		"""
		super(Actuals, self).__init__(start_position, end_position)
		self.expressions = expressions
	def print_string(self, current_level = 0, graphical = False):
		"""Print out a string representing the node

		current_level := the level of the node in the tree
		graphical := True if a graphical representation should be printed

		Returns the top node labels if graphical is True

		"""
		if not graphical:
			for expression in self.expressions:
				print "  " * current_level + "expression=>"
				expression.print_string(current_level + 1, graphical)
		else:
			nodes = []
			for expression in self.expressions:
				nodes.append(expression.print_string(graphical = graphical))
			return nodes

class Call(Node):
	cluster = 0
	anchor = 0
	printed = {}
	def __init__(self, start_position, end_position, procedure, actuals):
		"""Create a node

		start_position := the starting position of the node
		end_position := the ending position of the node
		procedure := the procedure to call
		actuals := the actuals of the call

		"""
		super(Call, self).__init__(start_position, end_position)
		self.procedure = procedure
		self.actuals = actuals
	def get_type(self):
		"""Get the type object of the node

		Returns the type object of the node

		"""
		return self.procedure.get_type()
	def executes_call(self):
		return True
	def print_string(self, current_level = 0, graphical = False):
		"""Print out a string representing the node

		current_level := the level of the node in the tree
		graphical := True if a graphical representation should be printed

		Returns the top node label if graphical is True

		"""
		if not graphical:
			print "  " * current_level + "Call ({}):".format(self.procedure.name)
			if self.actuals:
				print "  " * current_level + "actuals =>"
				self.actuals.print_string(current_level + 1, graphical)
		else:
			root = "node{}".format(Node.node)
			Node.node += 1
			print root, "[label=\"Call\",shape=rectangle]"
			if not self.procedure.name in Call.printed:
				procedure_label = "node{}".format(Node.node)
				Node.node += 1
				print procedure_label, "[label=\"{}()\"]".format(self.procedure.name)
				Call.printed[self.procedure.name] = procedure_label
				if self.procedure.instructions:
					instructions = self.procedure.instructions.print_string(graphical = graphical)
					print procedure_label, "->", instructions, "[label=\"instructions\"]"
			procedure = "node{}".format(Node.node)
			Node.node += 1
			print procedure, "[label=\"{}()\"]".format(self.procedure.name)
			print root, "->", procedure, "[label=\"procedure\"]"
			if self.actuals:
				nodes = self.actuals.print_string(graphical = graphical)
				print "subgraph cluster{}".format(Call.cluster), "{"
				Call.cluster += 1
				anchor = "anchor{}".format(Call.anchor)
				Call.anchor += 1
				print anchor, "[label=\"\",style=invis]"
				new_nodes = []
				for i, node in enumerate(nodes):
					new_node = "node{}".format(Node.node)
					Node.node += 1
					print new_node, "[label=\"{}\",shape=box,color=white,fontcolor=black]".format(self.procedure.formals[i][0].data)
					new_nodes.append(new_node)
				print "}"
				for i, new_node in enumerate(new_nodes):
					print new_node, "->", nodes[i]
				print root, "->", anchor, "[label=\"actuals\"]"
			return root

class AST_tree(object):
	def __init__(self, instructions):
		"""Create an abstract syntax tree

		instructions := the instructions in the program

		"""
		self.instructions = instructions
	def get_instructions(self):
		"""Get the instructions in the program

		Returns a list containing the instructions in the program

		"""
		return self.instructions.get_instructions()
	def print_tree(self, graphical = False):
		"""Print out a representation of the tree

		graphical := True if the representation should be graphical

		"""
		if graphical:
			print "Digraph x {"
		else:
			print "instructions =>"
		self.instructions.print_string(1, graphical)
		if graphical:
			print "}"

