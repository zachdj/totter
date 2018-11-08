import argparse
import json
import logging
import os
import sys

from totter.api.qwop import stop_qwop, QwopSimulator
from totter.evolution.GeneticAlgorithm import GeneticAlgorithm
from totter.evolution.QwopStrategy import QwopStrategy

# ---------------  IMPORT YOUR CUSTOM GAs HERE ---------------
from totter.evolution.algorithms.DoNothing import DoNothing
from totter.evolution.algorithms.ExampleGA import ExampleGA
from totter.evolution.algorithms.GoogleGA import GoogleGA


def main():
    logger = logging.getLogger('totter')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler(stream=sys.stdout))

    genetic_algorithms = dict()
    for algorithm in GeneticAlgorithm.__subclasses__():
        genetic_algorithms[algorithm.__name__] = algorithm

    parser = argparse.ArgumentParser(
        description='Totter: Evolutionary Computing for QWOP',
        argument_default=argparse.SUPPRESS,
    )

    parser.add_argument('--algorithm', default='ExampleGA', type=str, choices=list(genetic_algorithms.keys()),
                        help='The name of the GA that you would like to run.')

    subcommands = parser.add_subparsers()

    # evolution
    evolve = subcommands.add_parser('evolve', argument_default=argparse.SUPPRESS,
                                    description='Evolve solutions using the selected GA.')
    evolve.set_defaults(action='evolve')
    evolve.add_argument('--evaluations', type=int,
                        help='Maximum number of fitness evaluations before the algorithm terminates')
    evolve.add_argument('--eval_time_limit', type=int,
                        help='Maximum time (in seconds) that an individual is allowed to run before the simulation is '
                             'killed.')
    evolve.add_argument('--pop_size', type=int, help='Size of the population')
    evolve.add_argument('--cx_prob', type=float, help='Probability of crossover, expressed as a decimal')
    evolve.add_argument('--mt_prob', type=float, help='Probability of mutation, expressed as a decimal')
    evolve.add_argument('--generational', action='store_true',
                        help='If set, the GA will run in generational mode instead of steady-state mode')
    evolve.add_argument('--save_progress', action='store_true',
                        help='If set, the GA will save its current state in a "progress" file after completion')
    evolve.add_argument('--load', action='store_true',
                        help='If set, the GA will load its starting state from the latest saved progress file')

    # simulation
    simulate = subcommands.add_parser('simulate', argument_default=argparse.SUPPRESS,
                                    description='Play the game with the best solution discovered by the GA.')
    simulate.set_defaults(action='simulate')
    simulate.add_argument('--saved_result', type=str, help='Size of the population')

    args = parser.parse_args()
    args = vars(args)

    # every subparser has an action arg specifying which action to perform
    action = args.pop('action')
    # `args.algorithm` will be the name of one of the GA subclasses
    algorithm_name = args.pop('algorithm')
    algorithm_class = genetic_algorithms[algorithm_name]

    if action == 'evolve':
        evolution_config = {
            'evaluations': args['evaluations'] if 'evaluations' in args else 2000,
            'eval_time_limit': args['eval_time_limit'] if 'eval_time_limit' in args else 600,
            'pop_size': args['pop_size'] if 'pop_size' in args else 20,
            'cx_prob': args['cx_prob'] if 'cx_prob' in args else 0.9,
            'mt_prob': args['mt_prob'] if 'mt_prob' in args else 0.05,
            'steady_state': False if 'generational' in args else True
        }
        logger.info(f'Running GA {algorithm_name} with config:\n{evolution_config}')
        algorithm = algorithm_class(**evolution_config)

        # if the `load` flag was set, then load from the latest progress file
        if 'load' in args:
            algorithm.load()

        # run the ga
        time = algorithm.run()
        stop_qwop()

        # report results and save state
        logger.info(f'Evolution completed after {time}.\n Best solution found: {algorithm.best_indv}')
        if 'save_progress' in args:
            algorithm.save_current_state()
        save_path = algorithm.save_results()
        logger.info(f'Results saved to {save_path}')

    elif action == 'simulate':
        if 'saved_result' in args:
            filepath = args['saved_result']
        else:
            filepath = algorithm_class.get_results_path()

        if not os.path.exists(filepath):
            # if there is no results file, then we should quit
            logging.error(f'No results found for algorithm {algorithm_name} at {filepath}.\n'
                          f'Make sure you run evolve before using the simulate command.')
        else:
            # run the simulation
            with open(filepath, 'r') as results_file:
                data = json.load(results_file)

            best_genome = data['best_individual']
            algorithm = algorithm_class(pop_size=1)  # we just need a shell to get the execute method
            strategy = QwopStrategy(execution_function=algorithm.genome_to_phenotype(best_genome))
            simulator = QwopSimulator(time_limit=600)  # TODO: time limit is rather arbitrary
            simulator.simulate(strategy, qwop_started=True)
            stop_qwop()


if __name__ == '__main__':
    main()
