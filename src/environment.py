# Anthony Burzillo
# aburzil1@jhu.edu
#
# environment.py

import ast

class IntegerBox(object):
	def __init__(self):
		"""Creates a box for an integer

		Defaults the value of the integer to 0

		"""
		self.value = 0
	def copy(self):
		"""Create a copy of the integer

		Returns the copy IntegerBox

		"""
		new_box = IntegerBox()
		new_box.value = self.value
		return new_box
	def set_value(self, value):
		"""Set the value of the integer

		value := the value to set it to

		"""
		self.value = value
	def get_value(self):
		"""Get the value held by the box

		Returns the value

		"""
		return self.value

class ArrayBox(object):
	def __init__(self, size, type_instance = False):
		"""Create a box to hold an array

		size := the size of the array to be created
		type_instance := the box the array should hold

		"""
		self.size = size
		self.boxes = []
		if type_instance:
			for i in range(size):
				self.boxes.append(type_instance.copy())
	def copy(self):
		"""Copy the array

		Returns a copy of the ArrayBox

		"""
		new_box = ArrayBox(self.size)
		for box in self.boxes:
			new_box.boxes.append(box.copy())
		return new_box
	def set_to(self, box):
		"""Set the array equal to another array

		box := the ArrayBox to set the array to

		"""
		self.boxes = box.copy().boxes
	def get_box(self, index):
		"""Get the box at a certain index

		index := the index to get

		Returns False if index out of range, otherwise the box

		"""
		if index >= self.size:
			return False
		return self.boxes[index]

class RecordBox(object):
	def __init__(self, fields):
		"""Create a box for a record

		fields := a dictionary containing the name, box of each field

		"""
		self.fields = fields
	def copy(self):
		"""Copy the record object

		Returns the copied RecordBox

		"""
		fields = {}
		for field in self.fields:
			fields[field] = self.fields[field].copy()
		return RecordBox(fields)
	def set_to(self, box):
		"""Set the box equal to another record

		box := the RecordBox to set the record to

		"""
		self.fields = box.copy().fields
	def get_box(self, name):
		"""Get a box with a certain name

		name := the name to look for

		Returns false if the name is not in the records scope, otherwise the box

		"""
		if not name in self.fields:
			return False
		return self.fields[name]

class Environment(object):
	def __init__(self, table = False):
		"""Create an environment

		table := the Symbol_table to create an environment from

			"""
		if table:
			self.boxes = table.get_environment()
		else:
			self.boxes = False
	def get_box(self, name):
		"""Get the box with a certain name in the environment

		name := the name to look for

		Returns false if the name is not in the environment, otherwise the box

		"""
		if not name in self.boxes:
			return False
		return self.boxes[name]

