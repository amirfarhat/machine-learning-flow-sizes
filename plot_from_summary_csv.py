import csv
import click
import pickle
import matplotlib.pyplot as plt

from plot_cdf import add_cdf_to_plot

@click.command()
@click.option(
    "-s",
    "--summary-file",
    type=str,
    required=True,
    help="file containing the summary of iteration and flow data"
)
@click.option(
    "-m",
    "--model-name",
    type=str,
    required=True,
    help="name of the model we are summarizing"
)
def main(
    summary_file,
    model_name
):
    iteration_durations = []
    flow_sizes_in_iteration = []
    num_iters = -1 * float('inf')

    # populate iteration duration and flow size information
    with open(summary_file, newline='') as csvfile:
        # skip header
        next(csvfile, None)
        reader = csv.reader(csvfile, delimiter=',')
        for iteration_number, iteration_duration_seconds, flow_size_bytes_in_iteration in reader:
            num_iters = max(num_iters, int(iteration_number))
            iteration_durations.append(float(iteration_duration_seconds))
            flow_sizes_in_iteration.append(float(flow_size_bytes_in_iteration) / (10**9))

    # plot CDF of iteration durations
    # plt.subplot(211)
    # items, counts = add_cdf_to_plot(iteration_durations, plt)
    # plt.plot(items, counts)
    # plt.title('CDF of iteration durations from {} iterations of {} training\n'.format(num_iters, model_name))
    # plt.ylabel('% of iteration durations')
    # plt.xlabel('iteration duration in [second]')

    # plot CDF of flow sizes
    # plt.subplot(212)
    items, counts = add_cdf_to_plot(flow_sizes_in_iteration, plt)
    for i, c in zip(items, counts):
        print((i, c))
    plt.plot(items, counts)
    plt.title('CDF of flow size per iteration from {} iterations of {} training\n'.format(num_iters, model_name), fontdict={'fontsize':30})
    plt.ylabel('% of flow size size per iteration', fontsize=30)
    plt.xlabel('flow size size per iteration in [GB]', fontsize=30)
    plt.tick_params(axis='x', labelsize=30)
    plt.tick_params(axis='y', labelsize=30)

    plt.show()


if __name__ == '__main__':
    main()