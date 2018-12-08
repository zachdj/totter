import pathlib
import json
import statistics
import matplotlib.pyplot as plt

from totter.evolution.Experiment import plot as plot_history


def combine_trials(experiment_directory, std_dev_skip=15):
    exp_path = pathlib.Path(experiment_directory)
    metadata_file = exp_path / 'metadata.json'
    with open(metadata_file, 'r') as metadata_f:
        metadata = json.load(metadata_f)
    num_trials = metadata['trials']

    histories = list()
    for trial in range(1, num_trials+1):
        trial_data_file = exp_path / 'trials' / f'trial{trial}.json'
        with open(trial_data_file, 'r') as trial_data_f:
            trial_data = json.load(trial_data_f)
        trial_history = trial_data['history']
        histories.append(trial_history)

    # aggregate histories
    superhistory = list()
    last_std_dev_record = 0
    historical_data_points = len(histories[0])
    for i in range(historical_data_points):
        generation_counter, mbf, maf, std_dev = 0, 0, 0, 0
        mbfs = list()
        for history in histories:
            generation_counter = history[i][0]
            mbf += history[i][1]
            mbfs.append(history[i][1])
            maf += history[i][2]

        if num_trials > 1 and (i-last_std_dev_record) > std_dev_skip:
            std_dev = statistics.stdev(mbfs)  # standard deviation in mbf
            last_std_dev_record = i
        else:
            std_dev = 0
        mbf = mbf / num_trials  # mean best fitness
        maf = maf / num_trials  # mean average fitness

        entry = (generation_counter, mbf, maf, std_dev)
        superhistory.append(entry)

    # save the aggregate history
    history_path = exp_path / 'superhistory.json'
    with open(history_path, 'w') as history_file:
        json.dump(superhistory, history_file)

    # plot aggregate history and save the plot
    plot_history(superhistory)
    figure_path = exp_path / 'sampled_fitness_vs_time.png'
    plt.savefig(figure_path)


if __name__ == '__main__':
    combine_trials('../results/Experiment1/BitmaskGA')
    # combine_trials('/home/zach/Develop/totter/totter/results/Experiment1/BitmaskDurationGA')
    # combine_trials('/home/zach/Develop/totter/totter/results/Experiment1/KeystrokeGA')
    # combine_trials('/home/zach/Develop/totter/totter/results/Experiment1/KeyupKeydownGA')
