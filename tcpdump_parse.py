import pickle
import click
import matplotlib.pyplot as plt
import numpy as np
from fractions import Fraction
from pprint import pprint
from scapy.utils import RawPcapReader
from scapy.layers.l2 import Ether
from scapy.layers.inet import IP, TCP
from packet import Packet

kungfu_ips = {
    '10.128.0.55', 
    '10.128.0.54', 
    '10.128.0.53'
}

def build_packet(ip_pkt, pkt_metadata):
    # print(ip_pkt.show())

    # extract packet information
    pkt_size = int(ip_pkt.sprintf("%IP.len%"))
    pkt_seq = int(ip_pkt.sprintf("%TCP.seq%"))
    pkt_ack = int(ip_pkt.sprintf("%TCP.ack%"))
    pkt_flags = ip_pkt.sprintf("%TCP.flags%")
    pkt_timestamp = pkt_metadata.sec + (pkt_metadata.usec / 10**6)

    return Packet(timestamp=pkt_timestamp,
                  size_in_bytes=pkt_size,
                  src_address=ip_pkt.src,
                  src_port=ip_pkt.sport,
                  dst_address=ip_pkt.dst,
                  dst_port=ip_pkt.dport,
                  seq=pkt_seq,
                  ack=pkt_ack,
                  flags=pkt_flags)

def process_pcap(file_name):
    print('Opening {}...'.format(file_name))
    count = 0
    packets = []
    flows = dict()
    for (pkt_data, pkt_metadata,) in RawPcapReader(file_name):
        
        count += 1

        # get ethernet frame
        # and disregard non-IPv4 packets
        ether_pkt = Ether(pkt_data)
        if ether_pkt.type != 0x0800:
            continue

        # get ip packet from ethernet frame
        ip_pkt = ether_pkt[IP]
        if (ip_pkt.src in kungfu_ips) and (ip_pkt.dst in kungfu_ips):

            # build packet from given information
            packet = build_packet(ip_pkt, pkt_metadata)

            if packet.ack == 0:
                continue

            packets.append(packet)

            src_tuple = (packet.src_address, packet.src_port)
            dst_tuple = (packet.dst_address, packet.dst_port)
            flow_tuple = (src_tuple, dst_tuple)
            flows.setdefault(flow_tuple, [0, []])[1].append(packet)
            flows[flow_tuple][0] += packet.size_in_bytes
            
            # min_timestamp = min(min_timestamp, pkt_timestamp)
            # max_timestamp = max(max_timestamp, pkt_timestamp)
            # packets.append((pkt_timestamp, pkt_size))

        # use below line for debugging
        # full results from the tcpdump
        # require no breaking
        # if count == 10 ** 3: break

    print('Closing {}'.format(file_name))

    # sort packets in increasing timestamp order
    print('Sorting packets...')
    for flow_tuple in flows:
        flows[flow_tuple][1].sort(key = lambda pkt: pkt.timestamp)
    print('Sorted!')

    return packets, flows

@click.command()
@click.option(
    "-d",
    "--dump-file",
    type=str,
    required=True,
    help="filename of the tcpdump"
)
@click.option(
    "-p",
    "--do_pickle",
    is_flag=True,
    help="request to pickle the packet data"
)
def main(
    dump_file,
    do_pickle
):
    # parse all packets and construct flows
    packets, flows = process_pcap(dump_file)

    if do_pickle:
        pickle_name = dump_file.lstrip("pcaps/")
        with open('pickle/{}.pickle'.format(pickle_name), 'wb') as handle:
            print('Pickling...')
            pickle.dump(flows, handle, protocol=pickle.HIGHEST_PROTOCOL)
            print('Pickled!')

    # count = 0
    # for k, v in flows.items():
    #     count += 1
    #     flow_size, pkts = v

    #     print('Packet size sum: {}'.format(flow_size))
    #     min_ack = min(pkts, key = lambda pkt: pkt.ack).ack
    #     max_ack = max(pkts, key = lambda pkt: pkt.ack).ack
    #     print('Ack diff: {} - {} = {}'.format(max_ack, min_ack, max_ack - min_ack))
        
    #     timestamps = list(map(lambda pkt: pkt.timestamp, pkts))
    #     acks = list(map(lambda pkt: pkt.ack, pkts))

    #     plt.subplot(320 + count)
    #     plt.plot(timestamps, acks)
    # plt.show()


if __name__ == '__main__':
    main()

# print('{} has {} flows'.format(file_name, len(flows)))
# total_bytes = 0
# for i, flow_tuple in enumerate(flows.keys()):
#     srct, dstt = flow_tuple
#     flow_num = i+1
#     src, srcp = srct # src address and port
#     dst, dstp = dstt # dst address and port
#     sent_bytes, packets = flows[flow_tuple]
#     total_bytes += sent_bytes
#     sent_bytes = sent_bytes // 10**6
#     print('Flow {} {}:{} ~> {}:{} sent {} packets containing {} megabytes'.format(flow_num, src, srcp, dst, dstp, len(packets), sent_bytes))
# print('Total bytes sent: {} megabytes'.format(total_bytes // 10**6))

# with open('flow_dict_random.pickle', 'wb') as handle:
#     pickle.dump(flows, handle, protocol=pickle.HIGHEST_PROTOCOL)
#     print('Pickled!')

  
# x = []
# y = []
# mt = -1
# t_vals = []
# all_vals = []
# for i in range(1, len(thputs)):
#     # pull two points
#     t_curr_sec, p_curr_byte = thputs[i]
#     t_prev_sec, p_prev_byte = thputs[i-1]
#     # normalize time wrt min observed time
#     t_curr_normalized_sec = (t_curr_sec - min_timestamp)
#     t_prev_normalized_sec = (t_prev_sec - min_timestamp)
#     # convert packet sizes to bits
#     p_curr_bit = p_curr_byte * 8
#     p_prev_bit = p_prev_byte * 8
#     mt = max(mt, t_curr_normalized_sec)

#     t_vals.append(t_prev_normalized_sec)
#     all_vals.append((t_prev_normalized_sec, p_prev_bit))

# second_delta = Fraction(5, 10000)
# bins = [float(second_delta*(i+1)) for i in range(int(mt / second_delta))]
# bits_per_bin = [0 for _ in range(len(bins))]
# placements = np.digitize(t_vals, bins)

# for t_val_enum, p in zip(enumerate(t_vals), placements):
#     i, t_val = t_val_enum
#     bits_per_bin[p-1] += all_vals[i][1]

# plt.plot(bins, bits_per_bin)
# plt.ylabel('Thput in bits/second')
# plt.xlabel('Time in second')
# plt.title('Throughput of flows in ResNet50 training from {}'.format(file_name))
# plt.show()


