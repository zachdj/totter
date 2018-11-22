""" GAs that use the Bitmask + duration representation

"""

import copy
import pyautogui
import random
import time

from totter.evolution.GeneticAlgorithm import GeneticAlgorithm

CHARACTER_CODES = {
    'A': (True, True, True, True),
    'B': (True, True, True, False),
    'C': (True, True, False, True),
    'D': (True, True, False, False),

    'E': (True, False, True, True),
    'F': (True, False, True, False),
    'G': (True, False, False, True),
    'H': (True, False, False, False),

    'I': (False, True, True, True),
    'J': (False, True, True, False),
    'K': (False, True, False, True),
    'L': (False, True, False, False),

    'M': (False, False, True, True),
    'N': (False, False, True, False),
    'O': (False, False, False, True),
    'P': (False, False, False, False),
}


class BitmaskDurationGA(GeneticAlgorithm):

    def generate_random_genome(self):
        """ Representation - bitmask + duration

        An individual is a sequence of (bitmask, duration) pairs.  The bitmask one of the letters from the alphabet in CHARACTER_CODES.
        The duration specifies how long the bitmask should be held in milliseconds.
        For example, (A, 30) means hold all QWOP keys for 30 milliseconds

        Returns:
            Iterable<[str, int]>: Randomly generated genome

        """
        # initial length of the genome is chosen randomly from 10 - 30
        genome = list()
        genome_size = random.choice(range(10, 31))

        # for each position in the genome, choose a random bitmask and a random duration
        for i in range(genome_size):
            bitmask = random.choice(CHARACTER_CODES.keys())
            duration = random.uniform(100, 500)
            genome.append([bitmask, duration])

        return genome

    def genome_to_phenotype(self, genome):
        def phenotype():
            for key_code, duration in genome:
                bitmask = CHARACTER_CODES[key_code]
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
        """ Fitness: distance + speed """
        speed = distance_run*60 / run_time  # meters per minute
        if distance_run > 10:
            fitness = distance_run + speed
        else:
            fitness = distance_run
        return fitness

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
        """ Mutation - Either mutate one of the bitstrings or apply a gaussian shift to the duration """
        mutant = copy.deepcopy(genome)
        selected_gene = random.choice(range(len(mutant)))
        if random.random() < 0.5:
            # change to a different bitstring
            mutant[selected_gene][0] = random.choice(CHARACTER_CODES.keys())
        else:
            # apply gaussian perturbation to duration
            mutant[selected_gene][1] += random.gauss(0, 25)
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
