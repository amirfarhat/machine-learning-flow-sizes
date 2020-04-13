import click
import pickle
from pprint import pprint
from tqdm import tqdm

from hvd_analyze_iterations import get_iterations_list
from utils import scale_values

kungfu_ips = {
    '10.128.0.55', 
    '10.128.0.54', 
    '10.128.0.53',
    '10.128.0.52',
    '10.128.0.51',
    '10.138.0.42',
    '10.138.0.43',
    '10.138.0.44',
    '10.138.0.45',
}

valid_binning_strategies = {
    'slice',
    'squeeze'
}

is_kungfu = lambda x : x.startswith('10.128.0') or x.startswith('10.138.0')

def split_kungfu_host_and_port(raw_str):
    colon_at_end = raw_str[-1] == ':'

    host_ip = raw_str[:11]
    host_port = raw_str[12:-1] if colon_at_end else raw_str[12:]

    return (host_ip, host_port) 


def assign_packet_to_bin(packet, iterations, iteration_bins, min_iteration_start, max_iteration_end):
    # return if packet out of bounds
    pkt_timestamp, pkt_length = packet

    if pkt_timestamp < min_iteration_start:
        print('low sad: pkt_timestamp {} and min_iteration_start {}'.format(pkt_timestamp, min_iteration_start))
        return
    
    if pkt_timestamp > max_iteration_end:
        print('high sad: pkt_timestamp {} and max_iteration_end {}'.format(pkt_timestamp, max_iteration_end))
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
            r = mid - 1
        
        # case: pkt falls after iteration
        elif pkt_timestamp > iterations[mid].end_time:
            l = mid + 1

        else:
            print('shouldnot get here')
            print(iterations[mid])
            print(pkt_timestamp)

    print('never made it')


def scale_packets(packets, min_iteration_start, max_iteration_end):
    # adjust packet timstamps to fit into iteration duration
    timestamps = list(map(lambda pkt: pkt[0], packets))
    scaled_timestamps = scale_values(timestamps, min_iteration_start, max_iteration_end)

    # reconstruct same packets with new timestamps
    scaled_packets = []
    for i, new_timestamp in tqdm(enumerate(scaled_timestamps), total=len(scaled_timestamps), desc="Applying scaled timestamps..."):
        old_timestamp, old_size = packets[i]
        new_packet = (new_timestamp, old_size)
        scaled_packets.append(new_packet)
    
    return scaled_packets


def parse_flows(lines, iterations):
    flows = dict()
    
    for i, line in tqdm(enumerate(lines), total=len(lines), desc="Parsing flows..."):
        if line == "": 
            continue

        split_line = (timestamp, raw_src, raw_dst, length_keyword, length) = line.split()

        if not (is_kungfu(raw_src) and is_kungfu(raw_dst)):
            continue

        src_tuple = split_kungfu_host_and_port(raw_src)
        dst_tuple = split_kungfu_host_and_port(raw_dst)
        flow_tuple = (src_tuple, dst_tuple)

        if length_keyword != 'length':
            continue

        timestamp = float(timestamp)
        length = int(length)
        packet = (timestamp, length)

        if flow_tuple not in flows:
            flows[flow_tuple] = dict()
            flows[flow_tuple]['flow_size_bytes'] = 0
            flows[flow_tuple]['iteration_bins'] = [0 for _ in range(len(iterations))]
            flows[flow_tuple]['packets'] = []
            flows[flow_tuple]['min_packet_timestamp'] = float('inf')
            flows[flow_tuple]['max_packet_timestamp'] = -1 * float('inf')

        # update info about this flow
        flows[flow_tuple]['flow_size_bytes'] += length
        flows[flow_tuple]['packets'].append(packet)
        flows[flow_tuple]['min_packet_timestamp'] = min(timestamp, flows[flow_tuple]['min_packet_timestamp'])
        flows[flow_tuple]['max_packet_timestamp'] = max(timestamp, flows[flow_tuple]['max_packet_timestamp'])

    return flows


def validate_binning_strategy(strategy):
    if strategy not in valid_binning_strategies:
        raise Exception('Invalid binning strategy. Expected one of {}'.format(valid_binning_strategies))


@click.command()
@click.option(
    "-f",
    "--filtered_tcpdump_file_name",
    type=str,
    required=True,
    help="filename of the filtered tcpdump file"
)
@click.option(
    "-i",
    "--iterations-file",
    type=str,
    required=True,
    help="filename of the iterations data"
)
@click.option(
    "-o",
    "--output-file",
    type=str,
    required=True,
    help="filename of where to dump the data"
)
@click.option(
    "-s",
    "--binning-strategy",
    type=str,
    default="slice",
    help="strategy to assign packets to iteration bins via timestamps"
)
def main(
    filtered_tcpdump_file_name,
    iterations_file,
    output_file,
    binning_strategy
):
    # validate binning strategy
    validate_binning_strategy(binning_strategy)
    print('Using binning strategy: {}'.format(binning_strategy))

    # read in iteration data
    with open(iterations_file) as iter_file:
        # duration data about iterations
        iterations = get_iterations_list(iter_file.read())
        print('Loaded iterations')
        min_iteration_start = min(iterations, key=lambda it: it.start_time).start_time
        max_iteration_end = max(iterations, key=lambda it: it.end_time).end_time
        print('min_iteration_start: {}'.format(min_iteration_start))
        print('max_iteration_end: {}'.format(max_iteration_end))
        print('iteration duration: {}'.format(max_iteration_end - min_iteration_start))

    # read in simplified tcpdump output
    with open(filtered_tcpdump_file_name, 'r') as filtered_tcpdump_file:
        packet_lines = filtered_tcpdump_file.read().split("\n")
    


    """
    to squeeze, must find first data packet i
    with nonzero size
    
    and

    last data packet j with nonzero size

    then, we have the old range and new range, 
    and can scale the timestamp value of the packet
    appropriately
    """

    # parse the flows from raw packet lines
    flows = parse_flows(packet_lines, iterations)
        

    # scale packets to iterations and then assign them to bins
    for flow_tuple in flows:
        # extract flow info
        flow_size = flows[flow_tuple]['flow_size_bytes']
        packets = flows[flow_tuple]['packets']

        # adjust the packets depending on binning strategy
        if binning_strategy == 'slice':
            adjusted_packets = packets
        else:
            # squeeze the packets into the total iteration durations
            adjusted_packets = scale_packets(packets, min_iteration_start, max_iteration_end)
        
        flows[flow_tuple]['packets'] = adjusted_packets

        print('min packet timestamp: {}'.format(min(adjusted_packets, key=lambda pkt: pkt[0])[0]))
        print('max packet timestamp: {}'.format(max(adjusted_packets, key=lambda pkt: pkt[0])[0]))

        # assign packets to bins
        for packet in tqdm(adjusted_packets, total=len(adjusted_packets), desc="Assigning packets to bins..."):
            assign_packet_to_bin(packet, iterations, flows[flow_tuple]['iteration_bins'], min_iteration_start, max_iteration_end)
        

    pickle_name = filtered_tcpdump_file_name.lstrip("pcaps/")
    pickle_name = pickle_name.lstrip("simples/")
    pickle_name = pickle_name.lstrip("pickle/")
    with open(output_file, 'wb') as handle:
        print('Pickling...')
        pickle.dump(flows, handle, protocol=pickle.HIGHEST_PROTOCOL)
        print('Pickled!')
            



if __name__ == '__main__':
    main()