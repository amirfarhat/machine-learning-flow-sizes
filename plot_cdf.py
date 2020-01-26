import collections
import matplotlib.pyplot as plt

values = [1,2,3,4,5,5,5,5,6]

def add_cdf_to_plot(values, plt):
	# count frequency of items
	counter = collections.Counter(values)
	items, counts = (zip(*counter.items()))

	# get total count
	total_count = sum(counts)
	
	# make cdf data
	sorted_items = sorted(items)
	cumulative_counts = []
	running_count = 0
	for item in sorted_items:
		running_count += counter[item]
		cumulative_counts.append(100 * running_count / total_count)

	plt.plot(sorted_items, cumulative_counts)

