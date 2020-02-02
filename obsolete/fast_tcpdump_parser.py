import click
import matplotlib.pyplot as plt
from scapy.utils import RawPcapReader
from scapy.layers.l2 import Ether
from scapy.layers.inet import IP, TCP
from pprint import pprint
from tqdm import tqdm

from analyze_iterations import get_iterations_list
from utils import assign_packet_to_bin
from utils import flows_to_json

kungfu_ips = {
    '10.128.0.55', 
    '10.128.0.54', 
    '10.128.0.53'
}

def process_pcap(pcap_file, iterations, min_iteration_start, max_iteration_end):
    pkt_count = 0
    flows = dict()

    packets = RawPcapReader(pcap_file).read_all()
    for (pkt_data, pkt_metadata,) in tqdm(packets, total=len(packets)):
        
        # get ethernet frame and disregard non-IPv4 packets
        ether_pkt = Ether(pkt_data)
        if ether_pkt.type != 0x0800:
            continue

        # get ip packet from ethernet frame
        ip_pkt = ether_pkt[IP]
        if (ip_pkt.src in kungfu_ips) and (ip_pkt.dst in kungfu_ips):
            pkt_count += 1

            # extract packet information
            pkt_size = int(ip_pkt.sprintf("%IP.len%"))
            pkt_timestamp = pkt_metadata.sec + (pkt_metadata.usec / 10**6)
            src_tuple = (pkt_src_ip, pkt_src_port) = ip_pkt.src, ip_pkt.sport
            dst_tuple = (pkt_dst_ip, pkt_dst_port) = ip_pkt.dst, ip_pkt.dport
            flow_tuple = (src_tuple, dst_tuple)

            # instantiate new flow
            if flow_tuple not in flows:
                flows[flow_tuple] = dict()
                flows[flow_tuple]['flow_size_bytes'] = 0
                flows[flow_tuple]['iteration_bins'] = [0 for _ in range(len(iterations))]
                flows[flow_tuple]['min_packet_timestamp'] = float('inf')
                flows[flow_tuple]['max_packet_timestamp'] = -1 * float('inf')

            # update min and max packet timestamps
            flows[flow_tuple]['min_packet_timestamp'] = min(pkt_timestamp, flows[flow_tuple]['min_packet_timestamp'])
            flows[flow_tuple]['max_packet_timestamp'] = max(pkt_timestamp, flows[flow_tuple]['max_packet_timestamp'])

            # assign packet to this flow
            flows[flow_tuple]['flow_size_bytes'] += pkt_size
            assign_packet_to_bin(pkt_timestamp, pkt_size, iterations, flows[flow_tuple]['iteration_bins'], min_iteration_start, max_iteration_end)
            
        # if pkt_count == 10 ** 4:
        #     break

    return flows

@click.command()
@click.option(
    "-d",
    "--dump-file",
    type=str,
    required=True,
    help="filename of the tcpdump"
)
@click.option(
    "-i",
    "--iterations-file",
    type=str,
    required=True,
    help="filename of the iterations data"
)
@click.option(
    "-j",
    "--do_json",
    is_flag=True,
    help="request to json the flow data"
)
def main(
    dump_file,
    iterations_file,
    do_json
):
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

    # get data about flows
    flows = process_pcap(dump_file, iterations, min_iteration_start, max_iteration_end)
    json_flows = flows_to_json(flows)
    print(json_flows)
    # for flow_tuple in flows:
    #     print(flow_tuple, flows[flow_tuple])

if __name__ == '__main__':
    main()