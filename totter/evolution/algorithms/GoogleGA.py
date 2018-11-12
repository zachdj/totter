""" The best-performing GA described in the Google paper "Evolving QWOP Gaits"

Reference: https://storage.googleapis.com/pub-tools-public-publication-data/pdf/42902.pdf

Its representation is a string of characters from a 16-character alphabet.  Each character codes for a particular input
state that will be held for 150 ms.  This is essentially the same as our "bitmask" representation.

"""

import time
import copy

import pyautogui
import random
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


class GoogleGA(CellularGA):

    def generate_random_genome(self):
        # initial length of the genome is chosen randomly from 20 to 40
        genome_size = random.choice(range(20, 41))
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
        """ Fitness function
        The runner is only awarded a fitness if he manages not to fall over before the evaluation time limit
        The fitness is his speed in meters per minute
        """
        if distance_run >= 99 or run_time > self.eval_time_limit:
            minutes = run_time / 60
            return distance_run / minutes
        else:
            return 0

    def crossover(self, parent1, parent2):
        """ Cut-and-splice crossover """
        cut_point1 = random.choice(range(1, len(parent1) - 1))
        cut_point2 = random.choice(range(1, len(parent2) - 1))
        child1 = parent1[:cut_point1] + parent2[cut_point2:]
        child2 = parent2[:cut_point2] + parent1[cut_point1:]
        return child1, child2

    def mutate(self, genome):
        """ Random choice mutation - alter one character at random"""
        mutant = copy.deepcopy(genome)
        # choose a random keystroke
        new_keycode = random.choice(list(CHARACTER_CODES.keys()))
        index = random.choice(range(0, len(mutant)))
        mutant[index] = new_keycode

        return mutant

    def repair(self, genome):
        return genome

    def replace(self, population, candidate):
        """ Inverse tournament selection with k=3
        Offspring survives only if its better than all three
        """
        competitors = random.sample(population, 3)
        worst = min(competitors, key=lambda individual: individual.fitness)
        if candidate.fitness > worst.fitness:
            # find the index of the worst of the 3
            replacement_index = population.index(worst)
            return replacement_index
        else:
            return None
