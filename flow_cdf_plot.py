import pickle
import click
import matplotlib.pyplot as plt

from plot_cdf import add_cdf_to_plot

MIN_FLOW_SIZE_THRESHOLD_BYTES = 45 

@click.command()
@click.option(
    "-f",
    "--flow-pickle-file",
    type=str,
    required=True,
    help="pickle of file containing iteration+flow data"
)
def main(
    flow_pickle_file,
):
    # load flow data
    with open(flow_pickle_file, "rb") as raw_pickle:
        print('Opening pickle...')
        pickle_data = pickle.load(raw_pickle)
        print('Loaded!')

        iterations = pickle_data['iterations']
        flows = pickle_data['flows']

    # prepare plot
    plt.title('CDF of flow sizes in {} iterations of ResNet50 training\nDump file:{}'.format(len(iterations), flow_pickle_file))
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

        # scale iteration_bins sizes to GB
        GB_iteration_bins = []
        for size in iteration_bins:
            size_GB = size / 10 ** 9
            GB_iteration_bins.append(size_GB)

        add_cdf_to_plot(GB_iteration_bins, plt)
        useful_flow_count += 1
        # break

    plt.legend(tuple(flow_strs))
    # plt.savefig('plot_from_{}.png'.format(flow_pickle_file))
    plt.show()

if __name__ == '__main__':
    main()