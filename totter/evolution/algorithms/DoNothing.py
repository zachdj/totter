""" GA that does nothing.  This is handy for testing purposes. """

import random, copy
from totter.evolution.GeneticAlgorithm import GeneticAlgorithm
from totter.evolution.CellularGA import CellularGA


class DoNothing(GeneticAlgorithm):

    def generate_random_genome(self):
        return 0

    def genome_to_phenotype(self, genome):
        def phenotype():
            pass

        return phenotype

    def compute_fitness(self, distance_run, time):
        return 0

    def select_parents(self, population, n):
        parents = list()
        for i in range(0, n):
            parents.append(random.choice(population))

        return parents

    def crossover(self, parent1, parent2):
        return copy.deepcopy(parent1), copy.deepcopy(parent2)

    def mutate(self, genome):
        mutant = copy.deepcopy(genome)
        return mutant

    def repair(self, genome):
        return genome

    def replace(self, population, candidate):
        return None


class DoNothingCellular(CellularGA):

    def generate_random_genome(self):
        return 0

    def genome_to_phenotype(self, genome):
        def phenotype():
            pass

        return phenotype

    def compute_fitness(self, distance_run, time):
        return 0

    def crossover(self, parent1, parent2):
        return copy.deepcopy(parent1), copy.deepcopy(parent2)

    def mutate(self, genome):
        mutant = copy.deepcopy(genome)
        return mutant

    def repair(self, genome):
        return genome
