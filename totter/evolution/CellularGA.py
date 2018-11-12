""" Cellular Genetic Algorithm

Organizes populations across a grid and restricts crossover to the fittest neighbor.
Note that this GA ignores the `cx_prob` and the `generational` parameters.  Crossover is always performed and the GA is
also elitist generational.

"""

from abc import abstractmethod
import math

from totter.evolution.GeneticAlgorithm import GeneticAlgorithm, Individual
from totter.utils.time import WallTimer


class CellularGA(GeneticAlgorithm):
    def __init__(self,
                 evaluations=2000,
                 eval_time_limit=600,
                 pop_size=30,
                 cx_prob=1,
                 mt_prob=0.05,
                 steady_state=True,
                 seed_population=False,
                 random_seed=1234):

        super().__init__(evaluations, eval_time_limit, pop_size, cx_prob, mt_prob, steady_state, seed_population, random_seed)
        self.rows = int(math.floor(math.sqrt(self.pop_size)))
        self.cols = int(math.ceil(math.sqrt(self.pop_size)))
        # ensure population can be made into a grid:
        if self.rows * self.cols != self.pop_size:
            raise ValueError('Population cannot be made into a grid.  Aborting.')
        self.grid_population()

    def grid_population(self):
        population_grid = [self.population[i * self.cols:(i + 1) * self.cols] for i in range(0, self.rows)]
        self.population = population_grid

    def seed(self, pool_size, time_limit=60):
        super().seed(pool_size, time_limit)
        self.grid_population()

    def run(self):
        # ensure population has been evaluated and best_indv is up-to-date
        # this is necesary after a GA is constructed or after loading a GA from disk
        for column in self.population:
            for indv in column:
                if indv.fitness is None:
                    self._evaluate(indv)
                if self.best_indv.fitness is None or indv.fitness > self.best_indv.fitness:
                    self.best_indv = indv

        # time the run
        timer = WallTimer()
        while self.total_evaluations < self.max_evaluations:
            # iterate over population
            for row in range(0, self.rows):
                for col in range(0, self.cols):
                    parent1 = self.population[row][col]
                    # select the fittest neighbor as parent 2
                    left_neighbor = self.population[row][col-1]
                    parent2 = left_neighbor
                    right_neighbor = self.population[row][(col+1) % self.cols]
                    if right_neighbor.fitness > parent2.fitness:
                        parent2 = right_neighbor
                    top_neighbor = self.population[row-1][col]
                    if top_neighbor.fitness > parent2.fitness:
                        parent2 = top_neighbor
                    bottom_neighbor = self.population[(row+1) % self.rows][col]
                    if bottom_neighbor.fitness > parent2.fitness:
                        parent2 = bottom_neighbor

                    # produce a child
                    child_genome = self.crossover(parent1.genome, parent2.genome)[0]
                    # mutate the child
                    if self.mt_prob < child_genome:
                        child_genome = self.mutate(child_genome)

                    child_genome = self.repair(child_genome)
                    child = Individual(genome=child_genome)
                    self._evaluate(child)

                    # replace current cell if better
                    if child.fitness > parent1.fitness:
                        self.population[row][col] = child

                    # update best individual the GA has found so far
                    if self.best_indv is None or child.fitness > self.best_indv.fitness:
                        self.best_indv = child

            # record history
            if self.best_indv is not None:
                best_fitness = self.best_indv.fitness
                average_fitness = sum(map(lambda indv: indv.fitness, self.population)) / len(self.population)
                self.history.append([self.generations, best_fitness, average_fitness])

            self.generations += 1

        return timer.since()

    def select_parents(self, neighbors, n):
        """ Cellular GAs use their own selection mechanism"""
        pass

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
