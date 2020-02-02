from tqdm import tqdm

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
	for value in tqdm(values, total=len(values), desc="Scaling packet timestamps..."):
		try:
			new_value = (((value - current_min) * new_range) / current_range) + new_min_value
		except ZeroDivisionError:
			new_value = new_min_value
		scaled_values.append(new_value)

	return scaled_values



def assign_packet_to_bin(pkt_timestamp, pkt_length, iterations, iteration_bins, min_iteration_start, max_iteration_end):
    # return if packet out of bounds
    if pkt_timestamp < min_iteration_start:
        return
    
    if pkt_timestamp > max_iteration_end:
        return
    
    # binary search on iterations
    l = 0
    r = len(iterations) - 1

    while l <= r:
        mid = int((l+r) // 2)

        # case: pkt timestamp falls inside an iteration
        if iterations[mid].start_time <= pkt_timestamp <= iterations[mid].end_time:
            iteration_bins[mid] += pkt_length
            return

        # case: pkt falls before iteration
        elif pkt_timestamp < iterations[mid].start_time:
            l = mid + 1
        
        # case: pkt falls after iteration
        else:
            r = mid - 1



def flows_to_json(flows_dict):
	# turn flows to json format
	json_flows = []

	for flow_tuple in flows_dict:

		# flow metadata
		src_tuple, dst_tuple = flow_tuple
		src_ip, src_port = src_tuple
		dst_ip, dst_port = dst_tuple

		# flow data sizes
		flow_size = flows_dict[flow_tuple]['flow_size_bytes']
		iteration_bins = flows_dict[flow_tuple]['iteration_bins']

		# only keep nontrivial flows
		if flow_size == 0:
			continue

		# json object to be written
		flow_to_json = {
			'flow_src_ip': src_ip,
			'flow_src_port': src_port,
			'flow_dst_ip': dst_ip,
			'flow_dst_port': dst_port,
			'flow_size_bytes': flow_size,
			'flow_size_per_iteration': iteration_bins
		}
		json_flows.append(flow_to_json)

	return json_flows


def flows_from_pickle(pickle_file):
	pass











