import csv
import click
import pickle
import matplotlib.pyplot as plt

from plot_cdf import add_cdf_to_plot

@click.command()
@click.option(
    "-f",
    "--flows-pickle-file",
    type=str,
    required=True,
    help="filename of the pickle file containing flow info"
)
@click.option(
    "-o",
    "--output-csv-file",
    type=str,
    required=True,
    help="filename of the csv file where to dump the data"
)
def main(
    flows_pickle_file,
    output_csv_file
):
    # load flows
    with open(flows_pickle_file, "rb") as raw_pickle:
        flows = pickle.load(raw_pickle)

    # aggregate all flows' size per iteration 
    all_sizes_per_iteration = []
    for flow_tuple in flows:
        all_sizes_per_iteration.extend(flows[flow_tuple]['iteration_bins'])

    # calculate cdf
    all_sizes_per_iteration = sorted(s for s in all_sizes_per_iteration if s != 0)
    items, counts = add_cdf_to_plot(all_sizes_per_iteration)

    # write cdf to output csv file
    with open(output_csv_file, 'w') as csv_file:
        
        # open csv and write header
        fieldnames = ['bytes_per_iteration', 'cdf']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        # write the flow size value
        for i, c in zip(items, counts):
            writer.writerow({'bytes_per_iteration': i, 'cdf': c / 100})

    plt.plot(items, counts)
    plt.show()
# with open(flow_size_file_path) as flow_size_file:
#     model_flows = json.load(flow_size_file)

#     all_sizes_per_iteration = []

#     data_flows_counter = 0
#     for flow in model_flows:
#         flow_src = flow['flow_src_ip']
#         flow_dst = flow['flow_dst_ip']
#         flow_size_GB = flow['flow_size_bytes'] / 10**9
#         flow_size_per_iteration = flow['flow_size_per_iteration']
#         flow_size_GB_per_iteration = [s / 10**9 for s in flow_size_per_iteration]

#         all_sizes_per_iteration.extend(flow_size_per_iteration)

#         data_flows_counter += 1
#         flow_str = '{} flow #{}: {} ~~> {} sent {} GB'.format(model_name, data_flows_counter, flow_src, flow_dst, flow_size_GB)
#         flow_strs.append(flow_str)

#         disparity = flow_size_GB - sum(flow_size_GB_per_iteration)
#         print(flow_str)
#         print('Disparity: {} GB'.format(disparity))
#         print()

#     # calculate cdf
#     all_sizes_per_iteration = sorted(s for s in all_sizes_per_iteration if s != 0)
#     items, counts = add_cdf_to_plot(all_sizes_per_iteration)
#     for i, c in zip(items, counts):
#         # print((i, c))
#         writer.writerow({'bytes_per_iteration': i, 'cdf': c / 100})
    
#     plt.plot(items, counts)
#     plt.show()


if __name__ == '__main__':
    main()