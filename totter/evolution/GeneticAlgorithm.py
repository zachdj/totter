""" Abstract base class for a simple GA

This GA will always seek to maximize fitness

"""

from abc import abstractmethod
import os
import pickle
import random

from totter.api.qwop import QwopEvaluator, QwopStrategy
from totter.evolution.Individual import Individual
from totter.evolution.Population import Population
import totter.utils.storage as storage


class GeneticAlgorithm(object):
    def __init__(self,
                 eval_time_limit=240,
                 pop_size=20,
                 cx_prob=0.9,
                 mt_prob=0.05,
                 steady_state=True,
                 population_seed=None):

        self.eval_time_limit = eval_time_limit
        self.total_evaluations = 0
        self.qwop_evaluator = QwopEvaluator(time_limit=self.eval_time_limit)

        self.pop_size = pop_size
        self.cx_prob = cx_prob
        self.mt_prob = mt_prob
        self.steady_state = steady_state
        self.population_seed = population_seed

        if population_seed is None:
            # create a random population
            individuals = [Individual(self.generate_random_genome()) for i in range(0, self.pop_size)]
            for indv in individuals:
                self._evaluate(indv)
            self.population = Population(individuals)
        else:
            self.population = self.seed_population(population_seed, time_limit=60)

    def get_configuration(self):
        return {
            'eval_time_limit': self.eval_time_limit,
            'pop_size': self.pop_size,
            'cx_prob': self.cx_prob,
            'mt_prob': self.mt_prob,
            'steady_state': self.steady_state,
            'population_seed': self.population_seed
        }

    def seed_population(self, pool_size, time_limit):
        """ Creates a Population using the best runners from a pool of randomly-generated runners

        This selects the best `self.pop_size` Individuals from a pool of randomly generated individuals, using
        distance achieved as the selection criterion.
        If the seeding procedure has already been run, then the individuals will instead be loaded from disk.

        Args:
            pool_size (int): the size of the randomly generated pool from which the initial population will be drawn
            time_limit (int): time limit (in seconds) for each evaluation in the pool

        Returns:
            totter.evolution.Population.Population: Population seeded with good runners

        """
        population_filepath = storage.get(os.path.join(self.__class__.__name__, 'population_seeds'))
        population_file = os.path.join(population_filepath, f'seed_{pool_size}_{self.pop_size}.tsd')

        # if the population has not previously been seeded, then generate the seeded pop
        if not os.path.exists(population_file):
            # temporarily set time limit
            default_time_limit = self.qwop_evaluator.simulator.time_limit
            self.qwop_evaluator.simulator.time_limit = time_limit

            # generate pool of random individuals
            pool = [Individual(self.generate_random_genome()) for i in range(0, pool_size)]
            candidates = list()
            for indv in pool:
                # custom evaluation
                phenotype = self.genome_to_phenotype(indv.genome)
                strategy = QwopStrategy(execution_function=phenotype)
                distance, run_time = self.qwop_evaluator.evaluate(strategy)[0]
                indv.fitness = self.compute_fitness(distance, run_time)
                candidates.append((indv, distance))

            # sort by descending distance run
            sorted_candidates = sorted(candidates, key=lambda c: -c[1])
            # grab the ones who ran farthest
            best_indvs = sorted_candidates[:pool_size]
            best_indvs = list(map(lambda c: c[0], best_indvs))
            # save the individuals found
            with open(population_file, 'wb') as data_file:
                pickle.dump(best_indvs, data_file)

            # reset time limit to its normal value
            self.qwop_evaluator.simulator.time_limit = default_time_limit

        # load best_individuals from a file
        with open(population_file, 'rb') as data_file:
            best_indvs = pickle.load(data_file)

        return Population(best_indvs)

    def advance(self):
        """ Advances the GA by one generation

        For generational GAs, a generation will replace the entire population.
        For a steady-state GA, a generation will only replace two members of the population.

        Returns: None

        """
        # select parents
        if self.steady_state:
            parents = self.select_parents(self.population, 2)
        else:
            parents = self.select_parents(self.population, self.pop_size)

        # make children using crossover
        offspring = list()
        for parent1, parent2 in zip(parents[::2], parents[1::2]):
            if random.random() < self.cx_prob:
                child1_genome, child2_genome = self.crossover(parent1.genome, parent2.genome)
                offspring.append(child1_genome)
                offspring.append(child2_genome)

        # mutate then repair
        for idx in range(0, len(offspring)):
            child_genome = offspring[idx]
            if random.random() < self.mt_prob:
                child_genome = self.mutate(child_genome)

            child_genome = self.repair(child_genome)

            # even if the child wasn't mutated, his fitness needs to be re-evaluated
            child = Individual(genome=child_genome)
            self._evaluate(child)
            offspring[idx] = child

        # update population
        for child in offspring:
            # do replacement
            replacement_index = self.replace(self.population, child)
            if replacement_index is not None:
                self.population.replace(replacement_index, child)

    def _evaluate(self, individual):
        """ Evaluates an indvidual using the QwopEvaluator and updates the individual's fitness

        Args:
            individual (Individual): the indvidual to evaluate

        Returns: None

        """
        phenotype = self.genome_to_phenotype(individual.genome)
        strategy = QwopStrategy(execution_function=phenotype)
        distance, run_time = self.qwop_evaluator.evaluate(strategy)[0]
        individual.fitness = self.compute_fitness(distance, run_time)
        self.total_evaluations += 1

    @abstractmethod
    def generate_random_genome(self):
        """ Generates a random genome

        Returns:
            object: randomly generated genome

        """
        pass

    @abstractmethod
    def genome_to_phenotype(self, genome):
        """ Convert a genome to a function that plays QWOP

        For example, if the genome is [W, Q, P], then the phenotype might be a function that presses 'W',
        then presses 'Q', then presses 'P'.

        Returns:
            function: function that implements the strategy suggested by the genome

        """
        pass

    @abstractmethod
    def compute_fitness(self, distance_run, run_time):
        """ Computes an individual's fitness from the distance run and the time it took

        Args:
            distance_run (float): distance run in the QWOP simulator
            run_time (float): time in seconds that it took to run to `distance`

        Returns:
            float: computed fitness

        """
        pass

    @abstractmethod
    def select_parents(self, population, n):
        """ Selects `n` members for parenthood from `population`

        Args:
            population (totter.evolution.Population.Population):
                the current population
            n (int):
                the number of parents to select

        Returns:
            list<Individual>: the individuals selected for parenthood from the given population

        """
        pass

    @abstractmethod
    def crossover(self, parent1, parent2):
        """ Crossover parent1 with parent2 and generate two offspring

        Args:
            parent1 (iterable): the genome of the first parent
            parent2 (iterable): the genome of the second parent

        Returns:
            iterable, iterable: genome of child 1, genome of child 2

        """
        pass

    @abstractmethod
    def mutate(self, genome):
        """ Perform mutation on the provided genome

        Args:
            genome (object): genome to mutate

        Returns:
            object: mutated genome

        """
        pass

    @abstractmethod
    def repair(self, genome):
        """ Repair a genome after crossover or mutation

        Args:
            genome (object): genome to repair

        Returns:
            object: genome with repaired contents

        """
        pass

    @abstractmethod
    def replace(self, population, candidate):
        """ Select a member of the population which will be replaced by `candidate`

        This method should return the index of the population member to replace.
        It may also return None, which indicates that `candidate` should be discarded instead of replacing a member
        of the population

        Args:
            population (list<Individual>:
                list of Individuals in the population. Each individual has a genome and a fitness.

            candidate (Individual): Individual which will replace the selected member

        Returns:
            int or None:
                index of population member to be replaced by `candidate`,
                or None if the replacement should not occur

        """
        pass
