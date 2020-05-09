import os
import csv
import math
import click
import pickle
import matplotlib
import matplotlib.pyplot as plt

from tqdm import tqdm

from hvd_analyze_iterations import get_iterations_list
from plot_cdf import add_cdf_to_plot

CERBERUS_PATH = '/Users/amirfarhat/Desktop/machine-learning-flow-sizes/cerberus_experiments/'

FIGSIZE = (18, 10)
LABEL_SIZE = 20
FONT_SIZE = 20
ROTATION = 45
LEGEND_SIZE = 20

def do_for_model(model_name):
    print(model_name)
    model_dir = os.path.join(CERBERUS_PATH, model_name)

    # populate iteration durations and flow sizes
    durations = []
    flow_sizes = []
    summmary_file = os.path.join(model_dir, f'{model_name}_summary_of_iteration_and_flow_size.csv')
    with open(summmary_file) as csvfile:
        # skip header
        next(csvfile, None)
        reader = csv.reader(csvfile, delimiter=',')
        for _, iteration_duration_seconds, flow_size_bytes_in_iteration in reader:
            durations.append(float(iteration_duration_seconds))
            flow_sizes.append(float(flow_size_bytes_in_iteration))

    # return CDFs for iteration and flow
    dItems, dCounts = add_cdf_to_plot(durations)
    fItems, fCounts = add_cdf_to_plot(flow_sizes)
    return (dItems, dCounts), (fItems, fCounts)


def main():
    # get all model names
    models = dict()
    for d in os.listdir(CERBERUS_PATH):
        if os.path.isdir(os.path.join(CERBERUS_PATH, d)):
            models[d] = dict()

    # get CDFs for iteration duration and flow sizes for each model
    for m in models:
        (dItems, dCounts), (fItems, fCounts) = do_for_model(m)
        models[m]['dItems'] = dItems
        models[m]['dCounts'] = dCounts
        models[m]['fItems'] = fItems
        models[m]['fCounts'] = fCounts

    fig = plt.figure()
    plt.rc('xtick', labelsize=LABEL_SIZE)
    plt.rc('ytick', labelsize=LABEL_SIZE)

    # plot iteration durations
    plt.figure(1)
    _, ax1 = plt.subplots(figsize=FIGSIZE)
    ax1.ticklabel_format(useOffset=False, style='plain')
    ax1.set_ylabel('Percent of Iterations', fontsize=FONT_SIZE)
    ax1.set_xlabel('Iteration Duration (s)', fontsize=FONT_SIZE)
    ax1.set_xscale("log")
    ax1.xaxis.set_minor_formatter(matplotlib.ticker.StrMethodFormatter('{x:.1f}'))
    ax1.xaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter('{x:.1f}'))
    ax1.set_xlim(left=0.2, right=3.0)
    for m in models:
        ax1.plot(models[m]['dItems'], models[m]['dCounts'], label=m, linewidth=5)
    for tick in ax1.get_xticklabels(minor=True):
        tick.set_rotation(ROTATION)
    for tick in ax1.get_xticklabels(minor=False):
        tick.set_rotation(ROTATION)
    ax1.legend(fontsize=LEGEND_SIZE, loc='upper left')

    # plot flow size
    plt.figure(2)
    _, ax2 = plt.subplots(figsize=FIGSIZE)
    ax2.ticklabel_format(useOffset=False, style='plain')
    ax2.set_ylabel('Percent of Iterations', fontsize=FONT_SIZE)
    ax2.set_xlabel('Iteration Flow Size (MB)', fontsize=FONT_SIZE)
    ax2.set_xscale("log")
    ax2.xaxis.set_minor_formatter(matplotlib.ticker.StrMethodFormatter('{x:.0f}'))
    ax2.xaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter('{x:.0f}'))
    ax2.set_xlim(left=10, right=1500)
    for m in models:
        sizes = [s / 10**6 for s in models[m]['fItems']]
        ax2.plot(sizes, models[m]['fCounts'], label=m, linewidth=5)
    for tick in ax2.get_xticklabels(minor=True):
        tick.set_rotation(ROTATION)
    for tick in ax2.get_xticklabels(minor=False):
        tick.set_rotation(ROTATION)
    ax2.legend(fontsize=LEGEND_SIZE, loc='upper left')

    # save figures
    ax1.figure.savefig('iterations_cdf.png')
    ax2.figure.savefig('flow_size_cdf.png')
    

if __name__ == '__main__':
    main()