import csv
import click
import matplotlib.pyplot as plt

from plot_cdf import add_cdf_to_plot

@click.command()
@click.option(
    "-f",
    "--first-csv",
    type=str,
    required=True,
    help="first csv to use"
)
@click.option(
    "--first-label",
    type=str,
    required=True,
    help="label for first csv to use"
)
@click.option(
    "-s",
    "--second-csv",
    type=str,
    required=True,
    help="second csv to use"
)
@click.option(
    "--second-label",
    type=str,
    required=True,
    help="label for second csv to use"
)
def main(
    first_csv,
    first_label,
    second_csv,
    second_label,
):
    # set up plot
    plt.title('CDF Comparison of{} and {} bytes sent per iteration'.format(first_label, second_label))
    plt.ylabel('cdf of bytes sent per iteration')
    plt.xlabel('bytes sent per iteration')

    # collect cdf data from each file
    for csv_filename, label in [(first_csv, first_label), (second_csv, second_label)]:
        xs, ys = [], []
        with open(csv_filename, newline='') as csvfile:
            # skip header
            next(csvfile, None)
            reader = csv.reader(csvfile, delimiter=',')
            for bytes_per_iteration, cdf in reader:
                xs.append(float(bytes_per_iteration))
                ys.append(float(cdf))
        # plot the data
        plt.plot(xs, ys, label=label)
    
    plt.legend()
    plt.show()


if __name__ == '__main__':
    main()