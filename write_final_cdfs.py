import os
import csv
import pickle
import matplotlib.pyplot as plt

from tqdm import tqdm

from plot_cdf import add_cdf_to_plot


path = '/Users/amirfarhat/Desktop/machine-learning-flow-sizes/cachenet_experiments/'


def flows_from_pickle(flow_pickle_file):
    # load flow data
    with open(flow_pickle_file, "rb") as raw_pickle:
        print(f"Opening pickle {flow_pickle_file}...")
        pickle_data = pickle.load(raw_pickle)
        print("Opened!")
    
    # flows is a dict
    flows = pickle_data
    return flows


def write_flow_bytes_sent_csv(model_name, flow_sizes_bytes, flow_sizes_cdf):
    # determine output file
    cdfs_path = os.path.join(path, "cdfs")
    model_prefix = f"cdf_total_bytes_sent_{model_name}"
    output_file_path = f"{os.path.join(cdfs_path, model_prefix)}.csv"

    # write cdf to output csv file
    with open(output_file_path, 'w') as csv_file:
        
        # open csv and write header
        fieldnames = ['flow_bytes_sent', 'cdf']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        # write the flow size value
        for s, c in zip(flow_sizes_bytes, flow_sizes_cdf):
            writer.writerow({'flow_bytes_sent': s, 'cdf': c / 100})


def write_flow_size_per_iteration_bytes_csv(model_name, flow_sizes_per_iteration_bytes, flow_sizes_per_iteration_cdf):
    # determine output file
    cdfs_path = os.path.join(path, "cdfs")
    model_prefix = f"cdf_bytes_per_iteration_{model_name}"
    output_file_path = f"{os.path.join(cdfs_path, model_prefix)}.csv"

    # write cdf to output csv file
    with open(output_file_path, 'w') as csv_file:
        
        # open csv and write header
        fieldnames = ['flow_bytes_per_iteration_sent', 'cdf']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        # write the flow size value
        for s, c in zip(flow_sizes_per_iteration_bytes, flow_sizes_per_iteration_cdf):
            writer.writerow({'flow_bytes_per_iteration_sent': s, 'cdf': c / 100})


for model_name in sorted(os.listdir(path)):
    # skip the figures and cdf directory
    if model_name in { 'figures', 'cdfs' }: continue

    # # DEBUG: skip gpt-2 for fastness
    # if model_name == 'gpt2-744m': continue

    print(f"Processing {model_name}...")

    # only keep directories
    experiment_directory = os.path.join(path, model_name)
    if not os.path.isdir(experiment_directory): continue

    # record flow size across all flows of the model
    flow_sizes = []

    # record flow size per iteration across all flows of the model
    all_iteration_bins = []

    # open the flow pickle files
    flow_pickle_directory = os.path.join(experiment_directory, 'flow_pickles')
    slice_flow_directory = os.path.join(flow_pickle_directory, 'slice')
    for flow_pickle_filename in os.listdir(slice_flow_directory):
        
        # construct path to the flow pickle file
        flow_pickle_file_path = os.path.join(slice_flow_directory, flow_pickle_filename)

        # fetch flows from pickle
        flows = flows_from_pickle(flow_pickle_file_path)

        # add this flow's iteration bins to the total
        for flow_tuple in tqdm(flows, total=len(flows), desc=f"Accumulating {model_name} flows..."):
            
            # record total flow size
            flow_size = flows[flow_tuple]['flow_size_bytes']
            flow_sizes.append(flow_size)

            # record flow sizes per iteration
            iteration_bins_bytes = flows[flow_tuple]['iteration_bins']
            all_iteration_bins.extend(iteration_bins_bytes)

    # calculate flow total bytes sent cdf
    flow_sizes = sorted(s for s in flow_sizes if s != 0)
    items, counts = add_cdf_to_plot(flow_sizes)
    
    # write cdf of flow's bytes sent
    write_flow_bytes_sent_csv(model_name, items, counts)

    # calculate flow size per iteration cdf
    all_iteration_bins = sorted(s for s in all_iteration_bins if s != 0)
    items, counts = add_cdf_to_plot(all_iteration_bins)

    # write cdf of flow's bytes sent
    write_flow_size_per_iteration_bytes_csv(model_name, items, counts)


