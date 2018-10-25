""" Abstract base class for a simple GA

This GA will always seek to maximize fitness
"""

from abc import abstractmethod
import copy
import random

from totter.api.evaluation import QwopEvaluator
from totter.utils.time import WallTimer
from totter.evolution.QwopStrategy import QwopStrategy


class GeneticAlgorithm(object):
    def __init__(self,
                 evaluations=2000,
                 eval_time_limit=600,
                 pop_size=20,
                 cx_prob=0.9,
                 mt_prob=0.05,
                 steady_state=True,
                 seed=1234):

        self.random_seed = seed

        self.qwop_evaluator = QwopEvaluator(time_limit=eval_time_limit)

        self.pop_size = pop_size
        self.cx_prob = cx_prob
        self.mt_prob = mt_prob
        self.steady_state = steady_state

        # variables that track progress
        self.total_evaluations = 0
        self.max_evaluations = evaluations
        self.best_indv = None

    def save(self):
        """ TODO: serialize the current state of the algorithm to disk

        Returns:

        """
        pass

    def load(self):
        """ TODO: deserialize the latest saved state from disk

        Returns:

        """
        pass

    def run(self):
        """ Runs the GA until the maximum number of iterations is achieved

        Returns: time taken during the run (in seconds)

        """
        # seed RNG
        random.seed(self.random_seed)

        # create a random population
        population = [Individual(self.generate_random_genome()) for i in range(0, self.pop_size)]
        for indv in population:
            self._evaluate(indv)

        # time the run
        timer = WallTimer()
        while self.total_evaluations < self.max_evaluations:
            # select parents
            if self.steady_state:
                parents = self.select_parents(population, 2)
            else:
                parents = self.select_parents(population, self.pop_size)

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
                if self.best_indv is None or child.fitness > self.best_indv.fitness:
                    self.best_indv = child

            # update population
            for child in offspring:
                replacement_index = self.replace(population, child)
                if replacement_index is not None:
                    population[replacement_index] = child

        return timer.since()

    def _evaluate(self, individual):
        """ Evaluates an indvidual using the QwopEvaluator, updates the individual's fitness, and increments the counter

        Args:
            individual (Individual): the indvidual to evaluate

        Returns:

        """
        phenotype = self.genome_to_phenotype(individual.genome)
        strategy = QwopStrategy(execution_function=phenotype)
        distance, time = self.qwop_evaluator.evaluate(strategy)[0]
        individual.fitness = self.compute_fitness(distance, time)
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
    def compute_fitness(self, distance_run, time):
        """ Computes an individual's fitness from the distance run and the time it took

        Args:
            distance_run (float): distance run in the QWOP simulator
            time (float): time in seconds that it took to run to `distance`

        Returns:
            float: computed fitness

        """
        pass

    @abstractmethod
    def select_parents(self, population, n):
        """ Selects `n` members for parenthood from `population`

        Args:
            population (list): the current population
            n (int): the number of parents to select

        Returns:
            list<Individual>: the individuals selected for parenthood

        """
        pass

    @abstractmethod
    def crossover(self, parent1, parent2):
        """ Crossover parent1 with parent2 and generate two offspring

        Args:
            parent1: the genome of the first parent
            parent2: the genome of the second parent

        Returns:
            (object, object): (genome of child 1, genome of child 2)

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


class Individual:
    def __init__(self, genome):
        self.genome = genome
        self.fitness = None

    def clone(self):
        cloned_self = Individual(copy.deepcopy(self.genome))
        cloned_self.fitness = self.fitness
        return cloned_self

    def __str__(self):
        return f'Individual: {self.genome}\tFitness: {self.fitness}'

    def __len__(self):
        return len(self.genome)
