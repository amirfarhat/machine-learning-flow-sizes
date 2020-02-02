import pickle
import json
import matplotlib.pyplot as plt

from plot_cdf import add_cdf_to_plot

model_flow_size_data = [
	('resnet50', 'final_data/resnet50.json'),
	('vgg19', 'final_data/vgg19.json'),
]

num_iters = 1000
model_names = ','.join(name for name, _ in model_flow_size_data)
plt.title('CDF of flow sizes in {} iterations of {} training'.format(num_iters, model_names))
plt.ylabel('% of flow sizes per iteration')
plt.xlabel('flow size per iteration [GB per iteration]')

flow_strs = []
for model_name, flow_size_file_path  in model_flow_size_data:

	with open(flow_size_file_path) as flow_size_file:
		model_flows = json.load(flow_size_file)

	data_flows_counter = 0
	for flow in model_flows:
		flow_src = flow['flow_src_ip']
		flow_dst = flow['flow_dst_ip']
		flow_size_GB = flow['flow_size_bytes'] / 10**9
		flow_size_per_iteration = flow['flow_size_per_iteration']
		flow_size_GB_per_iteration = [s / 10**9 for s in flow_size_per_iteration]

		print(flow_size_GB, sum(flow_size_GB_per_iteration))

		# keep only nontrivial data flows larger
		# if flow_size_GB <= 4 * 10**-8:
		# if flow_size_GB <= 1:
		# 	continue

		data_flows_counter += 1
		flow_str = '{} flow #{}: {} ~~> {} sent {} GB'.format(\
					model_name, data_flows_counter, flow_src, flow_dst, flow_size_GB)
		flow_strs.append(flow_str)
		print(flow_str)

		add_cdf_to_plot(flow_size_GB_per_iteration, plt)

plt.legend(flow_strs)
plt.show()