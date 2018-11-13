""" Cellular Genetic Algorithm

Organizes populations across a grid and restricts crossover to the fittest neighbor.
Note that this GA ignores the `cx_prob` and the `generational` parameters.  Crossover is always performed and the GA is
also elitist generational.

"""

from abc import abstractmethod
import random

from totter.evolution.GeneticAlgorithm import GeneticAlgorithm, Individual


class CellularGA(GeneticAlgorithm):
    def __init__(self,
                 eval_time_limit=240,
                 pop_size=20,
                 cx_prob=0.9,
                 mt_prob=0.05,
                 steady_state=True,
                 population_seeding_pool=None,
                 seeding_time_limit=60):

        super().__init__(
            eval_time_limit,
            pop_size,
            cx_prob,
            mt_prob,
            steady_state,
            population_seeding_pool,
            seeding_time_limit
        )
        self.population = self.population.to_grid()  # convert to a gridded population

    def advance(self):
        # iterate over population
        for row in range(0, self.population.rows):
            for col in range(0, self.population.cols):
                parent1 = self.population.get_by_coords(row, col)
                # select the fittest neighbor as parent 2
                left_neighbor = self.population.get_by_coords(row, col-1)
                parent2 = left_neighbor
                right_neighbor = self.population.get_by_coords(row, col+1)
                if right_neighbor.fitness > parent2.fitness:
                    parent2 = right_neighbor
                top_neighbor = self.population.get_by_coords(row-1, col)
                if top_neighbor.fitness > parent2.fitness:
                    parent2 = top_neighbor
                bottom_neighbor = self.population.get_by_coords(row+1, col)
                if bottom_neighbor.fitness > parent2.fitness:
                    parent2 = bottom_neighbor

                # produce a child
                if random.random() < self.cx_prob:
                    child_genome = self.crossover(parent1.genome, parent2.genome)[0]
                else:
                    child_genome = parent1.genome

                # mutate the child
                if random.random() < self.mt_prob:
                    child_genome = self.mutate(child_genome)

                child_genome = self.repair(child_genome)
                child = Individual(genome=child_genome)
                self._evaluate(child)

                # replace current cell if better than both parents
                if child.fitness > parent1.fitness and child.fitness > parent2.fitness:
                    self.population.replace_by_coords(row, col, child)

    def select_parents(self, neighbors, n):
        """ Cellular GAs use their own selection mechanism"""
        pass

    def replace(self, population, candidate):
        """ Cellular GAs use their own replacement mechanism"""
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
