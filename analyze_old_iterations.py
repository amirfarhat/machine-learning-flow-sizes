import csv
import click
import collections
import numpy as np
import matplotlib.pyplot as plt
from pprint import pprint

from plot_cdf import add_cdf_to_plot

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
@click.option(
    "-o",
    "--output-time-cdf",
    type=str,
    required=True,
    help="output file .csv to put the CDF of iteration durations"
)
def main(
    iteration_logs,
    model_name,
    output_time_cdf
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

    # write csv for iteration durations
    items, counts = add_cdf_to_plot(lengths)
    with open(output_time_cdf, 'w') as csv_file:

        # open csv and write header
        fieldnames = ['iteration_duration_seconds', 'cdf']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        # write the flow size value
        for i, c in zip(items, counts):
            writer.writerow({'iteration_duration_seconds': i, 'cdf': c / 100})

    plt.show()


if __name__ == '__main__':
    main()