import pickle
import click
import matplotlib.pyplot as plt

from packet import Packet
from analyze_iterations import get_iterations_list
from plot_cdf import add_cdf_to_plot

from utils import scale_values

def assign_packet_to_bin(packet, iterations, iteration_bins, min_iteration_start, max_iteration_end):
    if packet.timestamp < min_iteration_start:
        return
    if packet.timestamp > max_iteration_end:
        return

    for i, iteration in enumerate(iterations):
        if iteration.start_time <= packet.timestamp <= iteration.end_time:
            iteration_bins[i] += packet.size_in_bytes
            break
            
def time_shifted_packet(pkt, shift):
    return packet_with_new_timestamp(pkt, pkt.timestamp + shift)

def packet_with_new_timestamp(pkt, new_timestamp):
    return Packet(timestamp=new_timestamp,
                  size_in_bytes=pkt.size_in_bytes,
                  src_address=pkt.src_address,
                  src_port=pkt.src_port,
                  dst_address=pkt.dst_address,
                  dst_port=pkt.dst_port,
                  seq=pkt.seq,
                  ack=pkt.ack,
                  flags=pkt.flags)

@click.command()
@click.option(
    "-p",
    "--pickle-file",
    type=str,
    required=True,
    help="pickle filename generated from the tcpdump"
)
@click.option(
    "-i",
    "--iterations-file",
    type=str,
    required=True,
    help="filename of the iterations data"
)
@click.option(
    "--no-squeeze",
    is_flag=True,
    help="do not squeeze the packets into the iteration intervals"
)
def main(
    pickle_file,
    iterations_file,
    no_squeeze
):
    # load iterations
    with open(iterations_file) as iter_file:
        iterations = get_iterations_list(iter_file.read())
        print('Loaded iterations')

    # duration data about iterations
    min_iteration_start = min(iterations, key=lambda it: it.start_time).start_time
    max_iteration_end = max(iterations, key=lambda it: it.end_time).end_time
    print('min_iteration_start: {}'.format(min_iteration_start))
    print('max_iteration_end: {}'.format(max_iteration_end))
    print('iteration duration: {}'.format(max_iteration_end - min_iteration_start))
     
    # prepare plot
    plt.title('CDF of flow sizes in {} iterations of ResNet50 training\nDump file:{}'.format(len(iterations), pickle_file))
    plt.ylabel('% of flow sizes per iteration')
    plt.xlabel('flow size per iteration [GB per iteration]')

    # load flows
    with open(pickle_file, "rb") as raw_pickle:
        print('Opening pickle...')
        flows = pickle.load(raw_pickle)
        print('Loaded!')

    flow_strs = []
    for i, flow_tuple in enumerate(flows):
        # flow identifiers
        src_tuple, dst_tuple = flow_tuple
        src_address, src_port = src_tuple
        dst_address, dst_port = dst_tuple
        # flow size and packets
        flow_size, packets = flows[flow_tuple]
        flow_str = 'Flow {}: {} ~~> {} sent {} GB'.format(i+1, src_address[-2:], dst_address[-2:], flow_size / 10**9)
        flow_strs.append(flow_str)
        print(flow_str)

        # min_timestamp = min(packets, key=lambda pkt: pkt.timestamp).timestamp
        # max_timestamp = max(packets, key=lambda pkt: pkt.timestamp).timestamp
        # print('min_timestamp: {}'.format(min_timestamp))
        # print('max_timestamp: {}'.format(max_timestamp))
        # print('timestamp span: {}'.format(max_timestamp - min_timestamp))

        # scaled packet timestamps to fit into iterations 
        if not no_squeeze:
            scaled_packets = []
            timestamps = list(map(lambda pkt: pkt.timestamp, packets))
            scaled_timestamps = scale_values(timestamps, min_iteration_start, max_iteration_end)
            print('min_scaled_timestamp: {}'.format(min(scaled_timestamps)))
            print('max_scaled_timestamp: {}'.format(max(scaled_timestamps)))
            for i, new_timestamp in enumerate(scaled_timestamps):
                new_packet = packet_with_new_timestamp(packets[i], new_timestamp)
                scaled_packets.append(new_packet)
            packets = scaled_packets

        # iteration bins for flow sizes ready for this flow
        iteration_bins = [0 for _ in range(len(iterations))]
        for packet in packets:
            assign_packet_to_bin(packet, iterations, iteration_bins, min_iteration_start, max_iteration_end)

        # scale sizes to GB
        sum_of_bins_bytes = 0
        new_iteration_bins = []
        for size in iteration_bins:
            sum_of_bins_bytes += size
            size_GB = size / 10 ** 9
            new_iteration_bins.append(size_GB)
        iteration_bins = new_iteration_bins

        # calculate flow size disparity
        disparity = flow_size - sum_of_bins_bytes
        print('Disparity between flow size and sum of bins: {} GB'.format(disparity / 10**9))

        # print(iteration_bins)
        add_cdf_to_plot(iteration_bins, plt)
        # break

    plt.legend(tuple(flow_strs))
    plt.savefig('plot_from_{}.png'.format(pickle_file))
    plt.show()


if __name__ == '__main__':
    main()
