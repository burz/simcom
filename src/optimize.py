# Anthony Burzillo
# aburzil1@jhu.edu
#
# optimize.py

def consolidate_multiple_labels(code):
	"""Remove labels that point to the same instruction

	code := A list containing the code for a program

	Returns a list containing the optimized code

	"""
	new_code = []
	replacements = []
	for i, line in enumerate(code):
		if not new_code:
			new_code.append(line)
			continue
		line_split = line.split()
		last_split = new_code[len(new_code) - 1].split()
		if len(last_split) is 1 and len(line_split) is 1:
			if last_split[0][len(last_split[0]) - 1] == ":" and line_split[0][len(line_split[0]) - 1] == ":":
				if last_split[0] == "main:":
					new_code.append(line)
				elif line_split[0][:2] == "__":
					new_code.pop()
					replacements.append((last_split[0][:len(last_split[0]) - 1], line_split[0][:len(line_split[0]) - 1]))
					new_code.append(line)
				else:
					replacements.append((line_split[0][:len(line_split[0]) - 1], last_split[0][:len(last_split[0]) - 1]))
			else:
				new_code.append(line)
		else:
			new_code.append(line)
	for replacement in replacements:
		old_code = new_code
		new_code = []
		for line in old_code:
			new_code.append(line.replace(replacement[0], replacement[1]))
	return new_code

def delete_unused_labels(code):
	"""Remove labels that are never used

	code := A list containing the code for a program

	Returns a list containing the optimized code

	"""
	used = []
	for line in code:
		line_split = line.split()
		if len(line_split) is 2 and line_split[1][0] == "_":
			used.append(line_split[1])
	new_code = []
	for line in code:
		line_split = line.split()
		if len(line_split) is 1 and line_split[0][0] == "_":
			if not line_split[0][:len(line_split[0]) - 1] in used:
				continue
		new_code.append(line)
	return new_code

