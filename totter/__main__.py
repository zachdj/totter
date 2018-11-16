import argparse
import json
import logging
import os
import pathlib
import sys

from totter.api.qwop import stop_qwop, QwopSimulator
from totter.evolution.GeneticAlgorithm import GeneticAlgorithm
from totter.evolution.Experiment import Experiment
from totter.api.qwop import QwopStrategy
import totter.utils.storage as storage
from totter.evolution.CellularGA import CellularGA

# ---------------  IMPORT YOUR CUSTOM GAs HERE ---------------
from totter.evolution.algorithms.DoNothing import DoNothing
from totter.evolution.algorithms.DoNothing import DoNothingCellular
from totter.evolution.algorithms.ExampleGA import ExampleGA
from totter.evolution.algorithms.BitmaskDurationGA import BitmaskDurationGA
from totter.evolution.algorithms.BitmaskGA import BitmaskGA
from totter.evolution.algorithms.GoogleGA import GoogleGA


def main():
    logger = logging.getLogger('totter')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler(stream=sys.stdout))

    genetic_algorithms = dict()
    for algorithm in GeneticAlgorithm.__subclasses__():
        if len(algorithm.__subclasses__()) == 0:
            genetic_algorithms[algorithm.__name__] = algorithm
    for algorithm in CellularGA.__subclasses__():
        genetic_algorithms[algorithm.__name__] = algorithm

    parser = argparse.ArgumentParser(
        description='Totter: Evolutionary Computing for QWOP',
        argument_default=argparse.SUPPRESS,
    )

    parser.add_argument('--algorithm', default='ExampleGA', type=str, choices=list(genetic_algorithms.keys()),
                        help='The name of the GA that you would like to run.')

    subcommands = parser.add_subparsers()

    # evolution - runs an experiment
    evolve = subcommands.add_parser('evolve', argument_default=argparse.SUPPRESS,
                                    description='Evolve solutions using the selected GA.')
    evolve.set_defaults(action='evolve')
    evolve.add_argument('--trials', type=int, default=1,
                        help='Number of trials to run.  '
                             'Each trial will run the GA for the specified number of evaluations.')
    evolve.add_argument('--evaluations', type=int, default=1000,
                        help='Maximum number of fitness evaluations before the algorithm terminates')
    evolve.add_argument('--eval_time_limit', type=int, default=180,
                        help='Maximum time (in seconds) that an individual is allowed to run before the simulation is '
                             'killed.')
    evolve.add_argument('--pop_size', type=int, default=30, help='Size of the population')
    evolve.add_argument('--cx_prob', type=float, default=0.9, help='Probability of crossover, expressed as a decimal')
    evolve.add_argument('--mt_prob', type=float, default=0.05, help='Probability of mutation, expressed as a decimal')
    evolve.add_argument('--generational', action='store_true',
                        help='If set, the GA will run in generational mode instead of steady-state mode')
    evolve.add_argument('--population_seeding_pool', type=int, default=None,
                        help='Size of pool used for seeding the initial population')
    evolve.add_argument('--seeding_time_limit', type=int, default=60,
                        help='The time limit used when constructing the seeded population')

    # population seeding
    seed = subcommands.add_parser('seed', argument_default=argparse.SUPPRESS,
                                  description='Seed the population of the selected algorithm.')
    seed.set_defaults(action='seed')
    seed.add_argument('--pool_size', type=int, help='Size of the random pool from which seeds will be drawn.')
    seed.add_argument('--pop_size', type=int, help='Number of individuals to be drawn out of the pool.')

    # simulation
    simulate = subcommands.add_parser('simulate', argument_default=argparse.SUPPRESS,
                                      description='Play the game with the best solution discovered by the GA.')
    simulate.set_defaults(action='simulate')
    simulate.add_argument('--saved_result', type=str, help='Path to the results file that should be used')

    args = parser.parse_args()
    args = vars(args)

    # every subparser has an action arg specifying which action to perform
    action = args.pop('action')
    # `args.algorithm` will be the name of one of the GA subclasses
    algorithm_name = args.pop('algorithm')
    algorithm_class = genetic_algorithms[algorithm_name]

    if action == 'evolve':
        evolution_config = {
            'eval_time_limit': args['eval_time_limit'],
            'pop_size': args['pop_size'],
            'cx_prob': args['cx_prob'],
            'mt_prob': args['mt_prob'],
            'steady_state': False if 'generational' in args else True,
            'population_seeding_pool': args['population_seeding_pool'],
            'seeding_time_limit': args['seeding_time_limit'],
        }
        evaluations = args['evaluations']
        trials = args['trials']
        logger.info(f'Running GA {algorithm_name} for {trials} trials with config:\n{evolution_config}')

        # setup the experiment
        experiment = Experiment(algorithm_class, evolution_config, evaluations, trials)
        output_directory = experiment.run()

        # report results and save state
        logger.info(f'Evolution completed.\n Results saved to: {output_directory}')

    elif action == 'seed':
        pool_size = args['pool_size'] if 'pool_size' in args else 500
        pop_size = args['pop_size'] if 'pop_size' in args else 30
        logger.info(f'Seeding algorithm {algorithm_class.__name__} '
                    f'using pool size {pool_size} and population size {pop_size}')
        algorithm = algorithm_class(pop_size=pop_size, population_seeding_pool=pool_size)
        logger.info('Done.')

    elif action == 'simulate':
        if 'saved_result' in args:
            filepath = args['saved_result']
        else:
            filepath = storage.get(algorithm_class.__name__) / 'solution.json'

        if not os.path.exists(filepath):
            # if there is no results file, then we should quit
            logging.error(f'No results found for algorithm {algorithm_name} at {filepath}.\n'
                          f'Make sure you run evolve before using the simulate command.')
        else:
            # run the simulation
            with open(filepath, 'r') as results_file:
                data = json.load(results_file)

            best_genome = data['best_genome']
            algorithm = algorithm_class(pop_size=0, skip_init=True)  # we just need a shell to get the execute method
            strategy = QwopStrategy(execution_function=algorithm.genome_to_phenotype(best_genome))
            simulator = QwopSimulator(time_limit=600)  # TODO: time limit is rather arbitrary
            simulator.simulate(strategy, qwop_started=True)
            stop_qwop()


if __name__ == '__main__':
    main()
