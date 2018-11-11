""" GAs that use the Bitmask + duration representation

"""

import copy
import pyautogui
import random
import time

from totter.evolution.GeneticAlgorithm import GeneticAlgorithm


class BitmaskDurationGA(GeneticAlgorithm):

    def generate_random_genome(self):
        """ Representation - bitmask + duration

        An individual is a sequence of (bitmask, duration) pairs.  The bitmask is a length-4 binary vector describing
        which keys should be held.  The duration specifies how long the bitmask should be held in milliseconds.
        For example, (1000, 30) means hold the Q key for 30 ms.

        Returns:
            Iterable<[str, int]>: Randomly generated genome

        """
        # initial length of the genome is chosen randomly from 10 - 30
        genome = list()
        genome_size = random.choice(range(10, 30))

        # for each position in the genome, generate a random bitmask and a random duration
        for i in range(genome_size):
            bitmask = list(random.choices([True, False], k=4))
            duration = random.uniform(10, 50)
            genome.append([bitmask, duration])

        return genome

    def genome_to_phenotype(self, genome):
        def phenotype():
            for bitmask, duration in genome:
                # apply bitmask
                if bitmask[0]: pyautogui.keyDown('q')
                else: pyautogui.keyUp('q')
                if bitmask[1]: pyautogui.keyDown('w')
                else: pyautogui.keyUp('w')
                if bitmask[2]: pyautogui.keyDown('o')
                else: pyautogui.keyUp('o')
                if bitmask[3]: pyautogui.keyDown('p')
                else: pyautogui.keyUp('p')

                # hold for duration
                time.sleep(duration / 1000)

        return phenotype

    def compute_fitness(self, distance_run, run_time):
        """ Fitness: distance - time_over_75s

        75 seconds is roughly the human record for completing QWOP.
        We only penalize the strategy if it exceeds this time.

        """
        if run_time >= 75 or distance_run >= 100:
            return distance_run - (run_time - 75)
        else:
            return distance_run

    def select_parents(self, population, n):
        """ Tournament selection with k=5 """
        parents = list()
        for i in range(0, n):
            competitors = random.sample(population, 5)
            winner = max(competitors, key=lambda individual: individual.fitness)
            parents.append(winner)

        return parents

    def crossover(self, parent1, parent2):
        """ 50% 2-point crossover, 50% cut-and-splice """
        if random.random() < 0.5:
            # 2-point crossover
            # we have to choose a crossover point smaller than the length of the shortest parent
            maximum_crossover_point = min(len(parent1), len(parent2)) - 1
            crossover_point1 = random.choice(range(1, maximum_crossover_point - 1))
            crossover_point2 = random.choice(range(crossover_point1+1, maximum_crossover_point))
            child1 = parent1[:crossover_point1] + parent2[crossover_point1:crossover_point2] + parent1[crossover_point2:]
            child2 = parent2[:crossover_point1] + parent1[crossover_point1:crossover_point2] + parent2[crossover_point2:]
            return child1, child2
        else:
            # cut-and-splice
            cut_point1 = random.choice(range(1, len(parent1)-1))
            cut_point2 = random.choice(range(1, len(parent2)-1))
            child1 = parent1[:cut_point1] + parent2[cut_point2:]
            child2 = parent2[:cut_point2] + parent1[cut_point1:]
            return child1, child2

    def mutate(self, genome):
        """ Mutation - Either flip a bit in one of the bitstrings or apply a gaussian shift to the duration """
        mutant = copy.deepcopy(genome)
        selected_gene = random.choice(range(len(mutant)))
        if random.random() < 0.5:
            # flip a bit in the bitstring
            i = random.choice([0, 1, 2, 3])
            mutant[selected_gene][0][i] = not mutant[selected_gene][0][i]
        else:
            # apply gaussian perturbation to duration
            mutant[selected_gene][1] += random.gauss(0, 7)
        return mutant

    def repair(self, genome):
        return genome

    def replace(self, population, candidate):
        """ Replacement - replace one of the five worst members of the population """
        # population is a list of `Individual` objects
        # sort in order of fitness
        sorted_pop = sorted(population, key=lambda individual: individual.fitness)
        # choose one of the five members with worst fitness
        replacement = random.choice(sorted_pop[0:5])

        # find the index of the chosen member
        replacement_index = population.index(replacement)
        return replacement_index
