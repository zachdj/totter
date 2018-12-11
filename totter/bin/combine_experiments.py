# utility script to plot the graphs for all experiments on one set of axes

import pathlib
import json
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

PALETTE = [
    ['#FF0000', '#7F0000'],  # red
    ['#6666FF', '#4747B2'],  # blue
    ['#FFD700', '#998100'],  # gold
    ['#B266B2', '#730073'],  # purple
    ['#4CA64C', '#006600'],  # green
    ['#40E0D0', '#207068'],  # turquoise
    ['#8EABBC', '#47555E'],  # blue-grey
]

LABEL_SIZE = 24
TICK_FONTSIZE = 24


def get_immediate_subdirectories(a_dir):
    return [name for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]


def combine_experiments(experiment_directory):
    exp_path = pathlib.Path(experiment_directory)
    experiment_names = get_immediate_subdirectories(experiment_directory)
    experiment_paths = [exp_path / name for name in experiment_names]

    # create a plot
    fig, ax = plt.subplots()
    plt.xticks(fontsize=TICK_FONTSIZE)
    plt.yticks(fontsize=TICK_FONTSIZE)
    # label the axes
    ax.set_xlabel("Fitness Evaluations", fontsize=LABEL_SIZE)
    ax.set_ylabel("Mean Best Fitness", fontsize=LABEL_SIZE)
    # make `generations` axis show integer labels
    ax = fig.gca()
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))

    # plot each experiment
    experiment_lines = list()
    for index, path in enumerate(experiment_paths):
        superhistory_file = path / 'superhistory.json'
        with open(superhistory_file) as superhistory_f:
            superhistory = json.load(superhistory_f)

        superhistory = np.array(superhistory)
        generations = superhistory[:, 0]    # fitness evaluations
        best = superhistory[:, 1]           # mbf
        average = superhistory[:, 2]        # maf
        std_dev = superhistory[:, 3]        # sigma in mbfs across all trials

        palette = PALETTE[index]
        mbf, = ax.plot(generations, best, color=palette[0], linewidth=4)
        std_dev = ax.vlines(generations, best - 0.5*std_dev, best + 0.5*std_dev, colors=palette[1])
        experiment_lines.append(mbf)

    # create a legend
    ax.legend(experiment_lines, experiment_names, loc='upper center', bbox_to_anchor=(0.5, 1.12), ncol=2,
              fancybox=True, shadow=True, fontsize=LABEL_SIZE)

    fig = plt.gcf()
    fig.set_size_inches(18.5, 11)
    fig.savefig(exp_path / 'fig.png', dpi=100)


if __name__ == '__main__':
    combine_experiments('/home/zach/Develop/totter/totter/results/Experiment5')
