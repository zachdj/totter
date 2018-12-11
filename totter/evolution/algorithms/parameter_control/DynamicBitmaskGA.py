import random

from totter.evolution.algorithms.parameter_control.DynamicGA import DynamicMutationGA
from totter.evolution.algorithms.BitmaskGA import BitmaskGA


class DynamicMutationBitmaskGA(DynamicMutationGA, BitmaskGA):
    pass


class DynamicReplacementBitmaskGA(BitmaskGA):
    def replace(self, population, candidate):

        # alpha starts at 0.5 and gradually increases to 2.0 as fitness evaluations approach 1000
        alpha = 0.5 + (1.5*self.total_evaluations/1000)

        # each individual's weight is the inverse of their fitness raised to the alpha power
        inverse_fitness = list(map(
            lambda indv: (1/abs(indv.fitness))**alpha if indv.fitness != 0 else 0.25,  # avoid division by zero errors
            population.individuals
        ))

        selected_indv = random.choices(population.individuals, weights=inverse_fitness)

        replacement_index = population.individuals.index(selected_indv[0])
        return replacement_index


class DynamicBitmaskGA(DynamicMutationGA, BitmaskGA):
    def replace(self, population, candidate):

        # alpha starts at 0.5 and gradually increases to 2.0 as fitness evaluations approach 1000
        alpha = 0.5 + (1.5*self.total_evaluations/1000)

        # each individual's weight is the inverse of their fitness raised to the alpha power
        inverse_fitness = list(map(
            lambda indv: (1/abs(indv.fitness))**alpha if indv.fitness != 0 else 0.25,  # avoid division by zero errors
            population.individuals
        ))

        selected_indv = random.choices(population.individuals, weights=inverse_fitness)

        replacement_index = population.individuals.index(selected_indv[0])
        return replacement_index