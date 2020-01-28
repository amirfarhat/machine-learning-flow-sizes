import click
import pickle
from pprint import pprint
from tqdm import tqdm

from analyze_iterations import get_iterations_list

kungfu_ips = {
    '10.128.0.55', 
    '10.128.0.54', 
    '10.128.0.53'
}

def split_kungfu_host_and_port(raw_str):
    colon_at_end = raw_str[-1] == ':'

    host_ip = raw_str[:11]
    host_port = raw_str[12:-1] if colon_at_end else raw_str[12:]

    # if host_port == 'ndmp':
    #     host_port = '10000'

    return (host_ip, host_port) 


def assign_packet_to_bin(packet, iterations, iteration_bins, min_iteration_start, max_iteration_end):
    # return if packet out of bounds
    pkt_timestamp, pkt_length = packet

    if pkt_timestamp < min_iteration_start:
        return
    
    if pkt_timestamp > max_iteration_end:
        return
    
    # binary search on iterations
    l = 0
    r = len(iterations) - 1

    while l <= r:
        mid = l + int((r - l) // 2); 

        # case: pkt timestamp falls inside an iteration
        if iterations[mid].start_time <= pkt_timestamp <= iterations[mid].end_time:
            iteration_bins[mid] += pkt_length
            return

        # case: pkt falls before iteration
        elif pkt_timestamp < iterations[mid].start_time:
            l = mid + 1
        
        # case: pkt falls after iteration
        else:
            r = mid - 1


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
def main(
    filtered_tcpdump_file_name,
    iterations_file,
):
    is_kungfu = lambda x : x.startswith('10.128.0')

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
        lines = filtered_tcpdump_file.read().split("\n")
    
    flows = dict()
    
    for i, line in tqdm(enumerate(lines), total=len(lines)):
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

        flows[flow_tuple]['flow_size_bytes'] += length
        assign_packet_to_bin(packet, iterations, flows[flow_tuple]['iteration_bins'], min_iteration_start, max_iteration_end)

    for flow_tuple, flow_obj in flows.items():
        flow_size = flow_obj['flow_size_bytes']
        flow_iteration_bins = flow_obj['iteration_bins']
        print(flow_tuple, flow_size, sum(flow_iteration_bins))
        
    pickle_name = filtered_tcpdump_file_name.lstrip("pcaps/")
    with open('pickle/newflows_simple_ahh{}.pickle'.format(pickle_name), 'wb') as handle:
        print('Pickling...')
        pickle.dump(flows, handle, protocol=pickle.HIGHEST_PROTOCOL)
        print('Pickled!')
            



if __name__ == '__main__':
    main()