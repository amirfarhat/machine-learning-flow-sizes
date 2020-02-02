import click
import matplotlib.pyplot as plt

from tqdm import tqdm

from analyze_iterations import get_iterations_list
from read_simple import parse_flows

def plot_points_1D(points, plt, val, **kwargs):
    plt.scatter(points, [val for _ in range(len(points))], **kwargs)

@click.command()
@click.option(
    "-f",
    "--filtered-dump-file",
    type=str,
    required=True,
    help="file containing the filtered tcpdump data"
)
@click.option(
    "-i",
    "--iterations-file",
    type=str,
    required=True,
    help="file containing the iteration data"
)
def main(
    filtered_dump_file,
    iterations_file,
):
    # load iterations data
    with open(iterations_file) as iter_file:
        iterations = get_iterations_list(iter_file.read())

    # load dump file
    with open(filtered_dump_file) as dump_file:
        packet_lines = dump_file.read().split("\n")

    # plot metadata
    plt.title('Timestamps of flows and training iteration\nDump file:{}'.format(filtered_dump_file))
    plt.ylabel('irrelevant axis')
    plt.xlabel('unix epoch time [seconds]')

    # labels for legend
    labels = []

    # plot iteration start and finish
    min_iteration_start = min(iterations, key=lambda it: it.start_time).start_time
    max_iteration_end = max(iterations, key=lambda it: it.end_time).end_time
    iters = [min_iteration_start, max_iteration_end]
    label = "iteration start and finish"
    labels.append(label)
    plot_points_1D(iters, plt, 0, s=150, color='red', marker='+', label=label)

    # parse flows from dump file and iterations data
    count = 0
    flows = parse_flows(packet_lines, iterations)
    for flow_tuple in flows:
        # keep nontrivial flows
        if flows[flow_tuple]['flow_size_bytes'] == 0:
            continue

        packets = flows[flow_tuple]['packets']
        timestamps = list(map(lambda pkt: pkt[0], packets))

        # plot flow packet timestamps
        count += 1
        label = "flow {} timestamps".format(count)
        labels.append(label)
        print('Flow {} has {} and sent {} bytes'.format(count, flow_tuple, flows[flow_tuple]['flow_size_bytes']))
        plot_points_1D(timestamps, plt, count, marker='+', label=label)
    

    # show plot
    plt.legend(labels)
    plt.show()

if __name__ == '__main__':
    main()