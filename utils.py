
def scale_values(values, new_min_value, new_max_value):

	# determine current range of values 
	# by finding min and max values
	current_max = max(values)
	current_min = min(values)
	current_range = current_max - current_min

	# new range determined by min and max
	new_range = new_max_value - new_min_value

	# scale each of the values
	scaled_values = []
	for value in values:
		try:
			new_value = (((value - current_min) * new_range) / current_range) + new_min_value
		except ZeroDivisionError:
			new_value = new_min_value
		scaled_values.append(new_value)

	return scaled_values