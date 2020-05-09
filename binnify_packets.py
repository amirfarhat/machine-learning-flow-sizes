import os
import math
import click
import pickle

from tqdm import tqdm

from hvd_analyze_iterations import get_iterations_list

MIN_FLOW_SIZE_BYTES = 10**9
CERBERUS_PATH = '/Users/amirfarhat/Desktop/machine-learning-flow-sizes/cerberus_experiments/'

def do_for_model(model_name):
    model_dir = os.path.join(CERBERUS_PATH, model_name)

    # read in iteration data
    iterations_file = os.path.join(model_dir, f'hvd_out_{model_name}')
    with open(iterations_file) as iter_file:
        iterations = get_iterations_list(iter_file.read())
        min_iteration_start = min(iterations, key=lambda it: it.start_time).start_time
        max_iteration_end = max(iterations, key=lambda it: it.end_time).end_time
        # print('Loaded iterations!')

    # read in all flow pickles
    flow_dicts = []
    pickle_dir = os.path.join(os.path.join(model_dir, 'flow_pickles'), 'slice')
    for p in os.listdir(pickle_dir):
        with open(os.path.join(pickle_dir, p), "rb") as raw_pickle:
            flow_dicts.append(pickle.load(raw_pickle))
    # print('Loaded flows!')

    total_packets, total_bytes = 0, 0
    count_before, count_inside, count_after = 0, 0, 0
    size_before, size_inside, size_after = 0, 0, 0

    for fd in flow_dicts:
        for f in fd.values():
            total_packets += len(f['packets'])
            total_bytes += f['flow_size_bytes']
            for pkt_timestamp, pkt_size in f['packets']:
                # case: before
                if pkt_timestamp < min_iteration_start:
                    count_before += 1
                    size_before += pkt_size
                # case: after
                elif pkt_timestamp > max_iteration_end:
                    count_after += 1
                    size_after += pkt_size
                # case: inside
                else:
                    count_inside += 1
                    size_inside += pkt_size

    sum_counts = count_before + count_inside + count_after
    sum_sizes = size_before + size_inside + size_after
    print()
    print(model_name)
    cbefore = round(100*count_before/total_packets, 2)
    cinside = round(100*count_inside/total_packets, 2)
    cafter  = round(100*count_after/total_packets, 2)
    sbefore = round(100*size_before/sum_sizes, 2)
    sinside = round(100*size_inside/sum_sizes, 2)
    safter  = round(100*size_after/sum_sizes, 2)
    print(f'PACKET COUNT | TOTAL {total_packets} BEFORE {count_before} | INSIDE {count_inside} | AFTER {count_after}')
    print(f'BYTES SUM    | TOTAL {total_bytes} BEFORE {size_before} | INSIDE {size_inside} | AFTER {size_after}')
    print(f"PACKETS | {cbefore}% before | {cinside}%inside | {cafter}%after")
    print(f"BYTES   | {sbefore}% before | {sinside}%inside | {int(100*size_after/sum_sizes)}%after")
    print()

def main():
    # get all model names
    model_names = []
    for d in os.listdir(CERBERUS_PATH):
        if os.path.isdir(os.path.join(CERBERUS_PATH, d)):
            model_names.append(d)

    for m in model_names:
        do_for_model(m)
        # break

if __name__ == '__main__':
    main()