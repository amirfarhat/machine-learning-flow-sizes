import pickle
import click
import matplotlib.pyplot as plt

from plot_cdf import add_cdf_to_plot

MIN_FLOW_SIZE_THRESHOLD_BYTES = 10**9

@click.command()
@click.option(
    "-f",
    "--flow-pickle-file",
    type=str,
    required=True,
    help="pickle of file containing iteration+flow data"
)
@click.option(
    "-m",
    "--model-name",
    type=str,
    required=True,
    help="name of the model we trained"
)
def main(
    flow_pickle_file,
    model_name
):
    # load flow data
    with open(flow_pickle_file, "rb") as raw_pickle:
        print('Opening pickle...')
        pickle_data = pickle.load(raw_pickle)
        print('Loaded!')

        flows = pickle_data

        for flow_tuple in flows:
            iterations_length = len(flows[flow_tuple]['iteration_bins'])
            break

    # prepare plot
    plt.title('CDF of flow sizes in {} iterations of {} training\nDump file:{}'.format(iterations_length, model_name, flow_pickle_file))
    plt.ylabel('% of flow sizes per iteration')
    plt.xlabel('flow size per iteration [GB per iteration]')

    # extract information from flow data
    useful_flow_count = 0
    flow_strs = []
    for flow_tuple in flows:
        # flow identifiers, size, and packets
        src_tuple, dst_tuple = flow_tuple
        src_address, src_port = src_tuple
        dst_address, dst_port = dst_tuple
        flow_size = flows[flow_tuple]['flow_size_bytes']
        iteration_bins = flows[flow_tuple]['iteration_bins']
        
        # flow size must be nontrivial
        if flow_size < MIN_FLOW_SIZE_THRESHOLD_BYTES:
            continue

        # formatted flow string
        flow_str = 'Flow {}: {} ~~> {} sent {} GB'.format(useful_flow_count+1, src_address[-2:], dst_address[-2:], flow_size / 10**9)
        flow_strs.append(flow_str)
        print(flow_str)

        bin_sum = sum(iteration_bins)
        print('Disparity: {} bytes'.format(flow_size - bin_sum))

        # scale iteration_bins sizes to GB
        GB_iteration_bins = []
        for size in iteration_bins:
            size_GB = size / 10 ** 9
            GB_iteration_bins.append(size_GB)

        add_cdf_to_plot(GB_iteration_bins, plt)
        useful_flow_count += 1

    plt.legend(tuple(flow_strs))
    plt.show()

if __name__ == '__main__':
    main()