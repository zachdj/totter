from abc import ABCMeta
import random
from totter.evolution.Individual import Individual
from totter.evolution.GeneticAlgorithm import GeneticAlgorithm


class DynamicMutationGA(GeneticAlgorithm, metaclass=ABCMeta):
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
            else:
                offspring.append(parent1.genome)
                offspring.append(parent2.genome)

        # mutate then repair
        for idx in range(0, len(offspring)):
            child_genome = offspring[idx]
            mt_prob = 1 - (1-self.mt_prob)*(self.total_evaluations/1000)
            if random.random() < mt_prob:
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