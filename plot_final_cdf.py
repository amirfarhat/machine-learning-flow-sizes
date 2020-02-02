import os
import pickle
import matplotlib.pyplot as plt

from tqdm import tqdm

from plot_cdf import add_cdf_to_plot


def flows_from_pickle(flow_pickle_file):
    # load flow data
    with open(flow_pickle_file, "rb") as raw_pickle:
        print(f"Opening pickle {flow_pickle_file}...")
        pickle_data = pickle.load(raw_pickle)
        print("Opened!")
    
    # flows is a dict
    flows = pickle_data
    return flows


path = '/Users/amirfarhat/Desktop/machine-learning-flow-sizes/cachenet_experiments/'

# prepare plot
plt.rcParams.update({'font.size': 30})
plt.ylabel('CDF')
plt.xlabel('Flow size per iteration [GB]')

for model_name in sorted(os.listdir(path)):
    # skip the figures directory
    if model_name == 'figures': continue

    # DEBUG: skip gpt-2 for fastness
    # if model_name == 'gpt2-744m': continue    

    print(f"Processing {model_name}...")

    # only keep directories
    experiment_directory = os.path.join(path, model_name)
    if not os.path.isdir(experiment_directory): continue

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
            # scale iteration_bins flow sizes to GB
            gigabyte_flow_iteration_bins = map(lambda s: s / 10**9, flows[flow_tuple]['iteration_bins'])
            all_iteration_bins.extend(gigabyte_flow_iteration_bins)

    # calculate cdf
    all_iteration_bins = sorted(s for s in all_iteration_bins if s != 0)
    items, counts = add_cdf_to_plot(all_iteration_bins)

    # normalize counts to CDF [0, 1]
    counts = [c / 100 for c in counts]
        
    # plot the flows' cdf for this model
    plt.plot(items, counts, linewidth=10.0, label=f"{model_name} flows")
    
# show legend and plot
plt.legend()
plt.show()