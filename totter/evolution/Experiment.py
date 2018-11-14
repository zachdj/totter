from datetime import datetime
import json
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import numpy as np
import os
import random
import statistics
import totter.utils.storage as storage
from totter.api.qwop import stop_qwop


class Experiment(object):
    def __init__(self, algorithm_class, algorithm_config, max_evaluations, trials):
        """ Experiments run a GA several times and report results

        Args:
            algorithm_class (class): class of the GeneticAlgorithm that should be run
            algorithm_config (dict): dictionary of named arguments that will be passed to the algorithm constructor
            max_evaluations (int): the maximum number of fitness evaluations to be performed during each run
            trials (int): number of trials to run

        """
        self.algorithm_class = algorithm_class
        self.algorithm_config = algorithm_config
        self.max_evaluations = max_evaluations
        self.trials = trials
        self.histories = list()

        self.results_directory = storage.get(os.path.join(algorithm_class.__name__))
        if not os.path.exists(self.results_directory):
            os.mkdir(self.results_directory)

        self.trials_directory = storage.get(os.path.join(algorithm_class.__name__, 'trials'))
        if not os.path.exists(self.trials_directory):
            os.mkdir(self.trials_directory)

    def run(self):
        best_solution_found = None
        # run each trial
        for i in range(1, self.trials+1):
            random.seed(i)
            best_indv = self._run_trial(i)
            stop_qwop()

            if best_solution_found is None or best_solution_found.fitness < best_indv.fitness:
                best_solution_found = best_indv

        # save the best individual found using this GA:
        best_soln_data = {
            'best_genome': best_solution_found.genome,
            'best_fitness': best_solution_found.fitness
        }
        solution_path = os.path.join(self.results_directory, 'solution.json')
        with open(solution_path, 'w') as soln_file:
            json.dump(best_soln_data, soln_file)

        # save metadata
        metadata = {
            'name': self.algorithm_class.__name__,
            'date': datetime.strftime(datetime.now(), '%Y-%m-%d_%H:%M'),
            'trials': self.trials,
            'config': self.algorithm_config
        }
        metadata_path = os.path.join(self.results_directory, 'metadata.json')
        with open(metadata_path, 'w') as md_file:
            json.dump(metadata, md_file)

        # aggregate histories
        superhistory = list()
        historical_data_points = len(self.histories[0])
        for i in range(historical_data_points):
            generation_counter, mbf, maf, std_dev = 0, 0, 0, 0
            mbfs = list()
            for history in self.histories:
                generation_counter = history[i][0]
                mbf += history[i][1]
                mbfs.append(history[i][1])
                maf += history[i][2]

            if self.trials > 1:
                std_dev = statistics.stdev(mbfs)  # standard deviation in mbf
            else:
                std_dev = 0
            mbf = mbf / self.trials  # mean best fitness
            maf = maf / self.trials  # mean average fitness

            entry = (generation_counter, mbf, maf, std_dev)
            superhistory.append(entry)

        # save the aggregate history
        history_path = os.path.join(self.results_directory, 'history.json')
        with open(history_path, 'w') as history_file:
            json.dump(superhistory, history_file)

        # plot aggregate history and save the plot
        plot(superhistory)
        figure_path = os.path.join(self.results_directory, 'fitness_vs_time.png')
        plt.savefig(figure_path)

        return self.results_directory

    def _run_trial(self, number):
        history = list()

        algorithm = self.algorithm_class(**self.algorithm_config)
        first_entry = (
            algorithm.total_evaluations,
            algorithm.population.best_fitness(),
            algorithm.population.mean_fitness(),
            algorithm.population.std_dev_fitness()
        )
        history.append(first_entry)

        while algorithm.total_evaluations < self.max_evaluations:
            algorithm.advance()
            entry = (
                algorithm.total_evaluations,
                algorithm.population.best_fitness(),
                algorithm.population.mean_fitness(),
                algorithm.population.std_dev_fitness()
            )
            history.append(entry)

        self.histories.append(history)

        # write the results of this trial
        data = {
            'name': self.algorithm_class.__name__,
            'trial': number,
            'config': algorithm.get_configuration(),
            'best_individual': algorithm.population.best_indv.genome,
            'best_fitness': algorithm.population.best_indv.fitness,
            'history': history
        }
        results_path = os.path.join(self.trials_directory, f'trial{number}.json')
        with open(results_path, 'w') as data_file:
            json.dump(data, data_file)

        # save the related plot
        plot(history)
        figure_path = os.path.join(self.trials_directory, f'trial{number}.png')
        plt.savefig(figure_path)

        return algorithm.population.best_indv


def plot(history):
    """ Generate a plot of fitness vs time given historical records

    Args:
        history (list): list of (generation, best fitness, avg fitness, std_deviation) tuples

    Returns: None

    """
    plt.clf()  # clear any old figures
    history = np.array(history)

    generations = history[:, 0]
    best = history[:, 1]
    average = history[:, 2]
    std_dev = history[:, 3]

    fig, ax1 = plt.subplots()
    # label the axes
    ax1.set_xlabel("Generation")
    ax1.set_ylabel("Fitness")
    # make `generations` axis show integer labels
    ax = fig.gca()
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    line1 = ax1.plot(generations, best, "b-", label="Best Fitness")
    line2 = ax1.plot(generations, average, "r-", label="Average fitness")

    # construct legend
    lns = line1 + line2
    labs = [l.get_label() for l in lns]
    ax1.legend(lns, labs, loc="center right")
