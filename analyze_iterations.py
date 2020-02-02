import click
import collections
import numpy as np
import matplotlib.pyplot as plt
from pprint import pprint

Iteration = collections.namedtuple('Iteration', [
	'number',
	'start_time', 
	'end_time'
])

def get_iterations_list(raw_text):
	# parse content into dictionary
	iterations_dict = dict()
	lines = raw_text.split('\n')
	for line in lines:
		tokens = line.split()
		if 'Unix' not in tokens: continue

		number = int(tokens[-2][1:-1])
		iterations_dict.setdefault(number, dict())['number'] = number
		
		time = float(tokens[-1])
		if 'before' in tokens:
			iterations_dict[number]['start_time'] = time
		elif 'after' in tokens:
			iterations_dict[number]['end_time'] = time

	# make list of `Iteration`s
	iterations = []
	for iter_number, iter_dict in iterations_dict.items():
		it = Iteration(number=iter_number,
					   start_time=iter_dict['start_time'],
					   end_time=iter_dict['end_time'])
		iterations.append(it)
	return iterations

@click.command()
@click.option(
    "-f",
    "--iteration-logs",
    type=str,
    required=True,
    help="filename of the output logs from training"
)
@click.option(
    "-m",
    "--model-name",
    type=str,
    required=True,
    help="name of the model we trained"
)
def main(
    iteration_logs,
    model_name
):
	# parse file into iterations
	with open(iteration_logs, 'r') as iter_file:
		raw_text = iter_file.read()
		iterations = get_iterations_list(raw_text)

	# fetch length of iterations
	numbers = list(map(lambda it: it.number, iterations))
	lengths = list(map(lambda it: it.end_time - it.start_time, iterations))

	# calculate stats
	avg_length = np.average(lengths)
	avg_text = 'Average duration of iterations is {} seconds'.format(avg_length)
	
	# plot iteration times
	plt.plot(numbers, lengths)
	plt.ylabel('Iteration duration in [second]')
	plt.xlabel('Iteration identifier [0-based index]')
	plt.title('Durations of {} iterations of {} training\n{}'.format(len(numbers), model_name, avg_text))
	plt.show()


if __name__ == '__main__':
	main()