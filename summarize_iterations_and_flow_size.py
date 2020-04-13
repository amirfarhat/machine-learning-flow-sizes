import os
import csv
import click
import pickle
import matplotlib.pyplot as plt

from tqdm import tqdm
from plot_cdf import add_cdf_to_plot
from hvd_analyze_iterations import get_iterations_list

path = '/Users/amirfarhat/Desktop/machine-learning-flow-sizes/cerberus_experiments/'


def flows_from_pickle(flow_pickle_file):
    # load flow data
    with open(flow_pickle_file, "rb") as raw_pickle:
        # print(f"Opening pickle {flow_pickle_file}...")
        pickle_data = pickle.load(raw_pickle)
        # print("Opened!")
    
    # flows is a dict
    flows = pickle_data
    return flows


def make_iterations_cdf_csv(model):
    iterfilename = f'hvd_out_{model}'
    model_dir = os.path.join(path, model)
    iteration_duration_outfile = f'{model}_iterations_cdf.csv'

    # parse file into iterations
    with open(os.path.join(model_dir, iterfilename), 'r') as iter_file:
        raw_text = iter_file.read()
        iterations = get_iterations_list(raw_text)
        lengths = list(map(lambda it: it.end_time - it.start_time, iterations))

    # write csv for iteration durations
    with open(os.path.join(model_dir, iteration_duration_outfile), 'w') as csv_file:
        items, counts = add_cdf_to_plot(lengths)
        # open csv and write header
        fieldnames = ['iteration_duration_seconds', 'cdf']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        # write the flow size value
        for i, c in zip(items, counts):
            writer.writerow({'iteration_duration_seconds': i, 'cdf': c / 100})

    return iterations


def make_flows_cdf_csv(model):
    model_dir = os.path.join(path, model)
    flow_cdf_csv_outfile = f'{model}_flow_size_per_iteration_cdf.csv'
    all_flows = []
    
    # add all relevant flows
    flow_size_per_iterations = []
    pickle_dir = os.path.join(model_dir, 'flow_pickles')
    slice_dir = os.path.join(pickle_dir, 'slice')
    for pickle_file_name in sorted(os.listdir(slice_dir)):
        # construct path to the flow pickle file
        flow_pickle_file_path = os.path.join(slice_dir, pickle_file_name)
        # fetch flows from pickle
        flows = flows_from_pickle(flow_pickle_file_path)
        for ft in flows:
            if flows[ft]['flow_size_bytes'] >= 10**9:
                all_flows.append(flows[ft])
                flow_size_per_iterations.extend(flows[ft]['iteration_bins'])
    
    # write csv of flow sizes
    with open(os.path.join(model_dir, flow_cdf_csv_outfile), 'w') as csv_file:
        items, counts = add_cdf_to_plot(flow_size_per_iterations)
        # open csv and write header
        fieldnames = ['bytes_per_iteration', 'cdf']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        # write the flow size value
        for i, c in zip(items, counts):
            writer.writerow({'bytes_per_iteration': i, 'cdf': c / 100})

    return all_flows


def make_iteration_and_flow_size_csv(model, iterations, all_flows):
    model_dir = os.path.join(path, model)
    summary_outfile = f'{model}_summary_of_iteration_and_flow_size.csv'

    # write csv of flow sizes
    with open(os.path.join(model_dir, summary_outfile), 'w') as csv_file:
        # open csv and write header
        fieldnames = ['iteration_number', 'iteration_duration_seconds', 'flow_size_bytes_in_iteration']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        # write rows
        for it in iterations:
            itdur = it.end_time - it.start_time
            for f in all_flows:
                fsize = f['iteration_bins'][it.number]
                writer.writerow({
                    'iteration_number': 1 + it.number,
                    'iteration_duration_seconds': itdur,
                    'flow_size_bytes_in_iteration': fsize,
                })


@click.command()
@click.option(
    "-m",
    "--model",
    type=str,
    required=True,
    help="model to summarize"
)
def main(
    model
):
    print(f'Model {model}')
    print('Making iterations csv...')
    iterations = make_iterations_cdf_csv(model)

    print('Making flows csv...')
    all_flows = make_flows_cdf_csv(model)

    print('Making summary csv...')
    make_iteration_and_flow_size_csv(model, iterations, all_flows)








if __name__ == '__main__':
    main()