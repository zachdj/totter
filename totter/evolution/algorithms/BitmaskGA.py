""" GAs that use the Bitmask representation

"""

import copy
import pyautogui
import random
import time

from totter.evolution.GeneticAlgorithm import GeneticAlgorithm
from totter.evolution.algorithms.parameter_control.DynamicGA import DynamicMutationGA
from totter.evolution.CellularGA import CellularGA

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


class BitmaskGA(GeneticAlgorithm):

    def generate_random_genome(self):
        """ Representation: sequence of bitmasks

        Each character in the first 16 letters of the alphabet represents a unique bitmask.  The genome is a sequence of
        these characters.  Each character will be held for 150 milliseconds

        """
        # initial length of the genome is chosen randomly from 10 to 21
        genome_size = random.choice(range(10, 21))
        # choose a random sequence of keystrokes of length `genome_size`
        genome = random.choices(list(CHARACTER_CODES.keys()), k=genome_size)

        return genome

    def genome_to_phenotype(self, genome):
        def phenotype():
            for key_code in genome:
                bitmask = CHARACTER_CODES[key_code]
                if bitmask[0]:
                    pyautogui.keyDown('q')
                else:
                    pyautogui.keyUp('q')
                if bitmask[1]:
                    pyautogui.keyDown('w')
                else:
                    pyautogui.keyUp('w')
                if bitmask[2]:
                    pyautogui.keyDown('o')
                else:
                    pyautogui.keyUp('o')
                if bitmask[3]:
                    pyautogui.keyDown('p')
                else:
                    pyautogui.keyUp('p')
                time.sleep(0.150)

        return phenotype

    def compute_fitness(self, distance_run, run_time):
        """ Fitness: distance + speed

        """
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
            competitors = random.sample(population.individuals, 5)
            winner = max(competitors, key=lambda individual: individual.fitness)
            parents.append(winner)

        return parents

    def crossover(self, parent1, parent2):
        """ 50% 2-point crossover, 50% cut-and-splice """
        if random.random() < 0.5:
            # 2-point crossover
            if len(parent1) < 3 or len(parent2) < 3:
                print(f'Skipping crossover.  Cannot perform 2-point xover with {parent1} and {parent2}')
                return parent1, parent2
            else:
                # we have to choose a crossover point smaller than the length of the shortest parent
                maximum_crossover_point = min(len(parent1), len(parent2)) - 1
                crossover_point1 = random.choice(range(0, maximum_crossover_point - 1))
                crossover_point2 = random.choice(range(crossover_point1+1, maximum_crossover_point))
                child1 = parent1[:crossover_point1] + parent2[crossover_point1:crossover_point2] + parent1[crossover_point2:]
                child2 = parent2[:crossover_point1] + parent1[crossover_point1:crossover_point2] + parent2[crossover_point2:]
                return child1, child2
        else:
            # cut-and-splice
            cut_point1 = random.choice(range(0, len(parent1)-1))
            cut_point2 = random.choice(range(0, len(parent2)-1))
            child1 = parent1[:cut_point1] + parent2[cut_point2:]
            child2 = parent2[:cut_point2] + parent1[cut_point1:]
            return child1, child2

    def mutate(self, genome):
        """ Mutation -
        Options:
            With 25% probability, change one of the characters to another randomly selected character
            With 25% probability, insert a random character at a random position
            With 25% probability, swap two characters
            With 25% probability, delete a randomly-selected character
        """
        mutant = copy.deepcopy(genome)
        selected_gene = random.choice(range(len(mutant)))
        decider = random.random()
        if decider < 0.25:
            # change to randomly selected character
            new_character = random.choice(list(CHARACTER_CODES.keys()))
            mutant[selected_gene] = new_character
        elif decider < 0.5:
            # insert random character
            new_character = random.choice(list(CHARACTER_CODES.keys()))
            mutant = mutant[:selected_gene] + [new_character] + mutant[selected_gene:]
        elif decider < 0.75:
            # swap two characters
            swap_pos = random.choice(range(len(mutant)))
            mutant[selected_gene], mutant[swap_pos] = mutant[swap_pos], mutant[selected_gene]
        else:
            # delete a gene
            if selected_gene != len(mutant) - 1:
                mutant = mutant[:selected_gene] + mutant[selected_gene+1:]
            else:
                mutant = mutant[:selected_gene]

        return mutant

    def repair(self, genome):
        if len(genome) <= 2:
            return genome[:] + genome[:]  # duplicate the genome so it can be used in crossover once again
        return genome

    def replace(self, population, candidate):
        """ Replacement - replace one of the five worst members of the population """
        # population is a list of `Individual` objectss
        # sort in order of fitness
        sorted_pop = sorted(population.individuals, key=lambda individual: individual.fitness)
        # choose one of the five members with worst fitness
        replacement = random.choice(sorted_pop[0:5])

        # find the index of the chosen member
        replacement_index = population.individuals.index(replacement)
        return replacement_index


# make a cellular version of the bitmask GA
# TODO: thus kinda sucks because we have to double-maintain everything
class CellularBitmaskGA(CellularGA):
    def generate_random_genome(self):
        """ Representation: sequence of bitmasks

        Each character in the first 16 letters of the alphabet represents a unique bitmask.  The genome is a sequence of
        these characters.  Each character will be held for 150 milliseconds

        """
        # initial length of the genome is chosen randomly from 10 to 21
        genome_size = random.choice(range(10, 21))
        # choose a random sequence of keystrokes of length `genome_size`
        genome = random.choices(list(CHARACTER_CODES.keys()), k=genome_size)

        return genome

    def genome_to_phenotype(self, genome):
        def phenotype():
            for key_code in genome:
                bitmask = CHARACTER_CODES[key_code]
                if bitmask[0]:
                    pyautogui.keyDown('q')
                else:
                    pyautogui.keyUp('q')
                if bitmask[1]:
                    pyautogui.keyDown('w')
                else:
                    pyautogui.keyUp('w')
                if bitmask[2]:
                    pyautogui.keyDown('o')
                else:
                    pyautogui.keyUp('o')
                if bitmask[3]:
                    pyautogui.keyDown('p')
                else:
                    pyautogui.keyUp('p')
                time.sleep(0.150)

        return phenotype

    def compute_fitness(self, distance_run, run_time):
        """ Fitness: distance + speed

        """
        speed = distance_run*60 / run_time  # meters per minute
        if distance_run > 10:
            fitness = distance_run + speed
        else:
            fitness = distance_run
        return fitness

    def crossover(self, parent1, parent2):
        """ 50% 2-point crossover, 50% cut-and-splice """
        if random.random() < 0.5:
            # 2-point crossover
            if len(parent1) < 3 or len(parent2) < 3:
                print(f'Skipping crossover.  Cannot perform 2-point xover with {parent1} and {parent2}')
                return parent1, parent2
            else:
                # we have to choose a crossover point smaller than the length of the shortest parent
                maximum_crossover_point = min(len(parent1), len(parent2)) - 1
                crossover_point1 = random.choice(range(0, maximum_crossover_point - 1))
                crossover_point2 = random.choice(range(crossover_point1+1, maximum_crossover_point))
                child1 = parent1[:crossover_point1] + parent2[crossover_point1:crossover_point2] + parent1[crossover_point2:]
                child2 = parent2[:crossover_point1] + parent1[crossover_point1:crossover_point2] + parent2[crossover_point2:]
                return child1, child2
        else:
            # cut-and-splice
            cut_point1 = random.choice(range(0, len(parent1)-1))
            cut_point2 = random.choice(range(0, len(parent2)-1))
            child1 = parent1[:cut_point1] + parent2[cut_point2:]
            child2 = parent2[:cut_point2] + parent1[cut_point1:]
            return child1, child2

    def mutate(self, genome):
        """ Mutation -
        Options:
            With 25% probability, change one of the characters to another randomly selected character
            With 25% probability, insert a random character at a random position
            With 25% probability, swap two characters
            With 25% probability, delete a randomly-selected character
        """
        mutant = copy.deepcopy(genome)
        selected_gene = random.choice(range(len(mutant)))
        decider = random.random()
        if decider < 0.25:
            # change to randomly selected character
            new_character = random.choice(list(CHARACTER_CODES.keys()))
            mutant[selected_gene] = new_character
        elif decider < 0.5:
            # insert random character
            new_character = random.choice(list(CHARACTER_CODES.keys()))
            mutant = mutant[:selected_gene] + [new_character] + mutant[selected_gene:]
        elif decider < 0.75:
            # swap two characters
            swap_pos = random.choice(range(len(mutant)))
            mutant[selected_gene], mutant[swap_pos] = mutant[swap_pos], mutant[selected_gene]
        else:
            # delete a gene
            if selected_gene != len(mutant) - 1:
                mutant = mutant[:selected_gene] + mutant[selected_gene+1:]
            else:
                mutant = mutant[:selected_gene]

        return mutant

    def repair(self, genome):
        if len(genome) <= 2:
            return genome[:] + genome[:]  # duplicate the genome so it can be used in crossover once again
        return genome


class FitnessReplacementBitmaskGA(BitmaskGA):
    """
    Bitmask GA but with inverse fitness-proportionate selection
    """
    def replace(self, population, candidate):
        # each individual's weight is the inverse of their fitness
        inverse_fitness = list(map(
            lambda indv: 1/abs(indv.fitness) if indv.fitness != 0 else 0.25,  # avoid division by zero errors
            population.individuals
        ))

        selected_indv = random.choices(population.individuals, weights=inverse_fitness)

        replacement_index = population.individuals.index(selected_indv[0])
        return replacement_index
