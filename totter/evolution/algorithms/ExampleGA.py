""" This file intends to provide a helpful example of how to create a custom QWOP GA """

""" Step 1: Imports
Import the libraries required for your GA.
In most cases, you'll at leat need the base class and pyautogui.  
pyautogui is a Python automation library that allows programmatic control of the mouse and keyboard.
I also import Python's random module, which provides an RNG, plus a few other utilities
"""


import time
import copy

import pyautogui
import random
from totter.evolution.GeneticAlgorithm import GeneticAlgorithm


""" Step 2: Create your GA by inheriting from GeneticAlgorithm """
class ExampleGA(GeneticAlgorithm):

    """ Step 3: Representation
    This function determines the representation used by your algorithm.  It should return a randomly-initialized genome.
    In this case, I'm using a very simple representation: a sequence of single keystrokes, either Q, W, O, or P.
    I assumed that each keystroke will be pressed for 20 milliseconds.
    """
    def generate_random_genome(self):
        # initial length of the genome is chosen randomly from 10, 30
        genome_size = random.choice(range(10, 30))
        # choose a random sequence of keystrokes of length `genome_size`
        genome = random.choices(['q', 'w', 'o', 'p'], k=genome_size)

        return genome

    """ Step 4: Translation 
    You need to provide a method which translates a genome to a function which plays the game.
    NOTE: this method must return a CALLABLE FUNCTION which executes the moves to play the game.
    
    In this case, the function will simply press the sequence of keystrokes suggested by the genome
    """
    def genome_to_phenotype(self, genome):
        def phenotype():
            for key in genome:
                pyautogui.keyDown(key)
                time.sleep(0.020)  # press for 20 milliseconds
                pyautogui.keyUp(key)

        return phenotype

    """ Step 5: Fitness Function
    Specify a function that computes fitness given the distance run and the time required to go that distance.
    The GA will seek to maximize fitness.
    
    In this case, fitness is simply the distance run
    """
    def compute_fitness(self, distance_run, run_time):
        return distance_run

    """ Step 6: Parenthood selectioin 
    Specify a function that selects `n` parents from the population of individuals.
    Each individual in the population is guaranteed to have a `fitness` attribute and a `genome` attribute.
    
    In this case, we use deterministic tournament selection with tournament size 5
    """
    def select_parents(self, population, n):
        parents = list()
        for i in range(0, n):
            competitors = random.sample(population.individuals, 5)
            winner = max(competitors, key=lambda individual: individual.fitness)
            parents.append(winner)

        return parents

    """ Step 7: Crossover 
    Specify the crossover function used by your GA.
    This function should take two parent genomes and returns two genomes that represent the children
    
    In this case, we use single-point crossover
    """
    def crossover(self, parent1, parent2):
        # we have to choose a crossover point smaller than the length of the shortest parent
        maximum_crossover_point = min(len(parent1), len(parent2)) - 1
        crossover_point = random.choice(range(1, maximum_crossover_point))  # pick a random crossover point
        child1 = parent1[:crossover_point] + parent2[crossover_point:]
        child2 = parent1[crossover_point:] + parent2[:crossover_point]
        return child1, child2

    """ Step 8: Mutation 
    Specify the mutation operation used by your GA.
    It should take a single genome and return a mutated version of that genome.
    
    In this case, we are using two different mutations.  50% of the time, we append a new random keystroke to the end
    of the sequence.  The other 50%, we randomly change one of the keystrokes in the sequence.
    """
    def mutate(self, genome):
        mutant = copy.deepcopy(genome)
        # choose a random keystroke
        new_keystroke = random.choice(['q', 'w', 'o', 'p'])
        if random.random() < 0.5:
            # add keystroke to the end of the sequence
            mutant.append(new_keystroke)
        else:
            # change existing keystroke
            index = random.choice(range(0, len(mutant)))
            mutant[index] = new_keystroke

        return mutant

    """ Step 9: Repair 
    If your algorithm makes use of a repair operator, specify it here.  The repair operator should take a genome
    and return a repaired version of the genome.
    
    In this case, we don't use a repair operator, so we just use the identity function.
    """
    def repair(self, genome):
        return genome

    """ Step 10: Replacement Selection 
    Specify a method which chooses a member of the population for replacement.  
    This method takes two arguments, `population` and `candidate`.  It should return the index of the population member 
    to replace with `candidate`.
    It may also return None, which indicates that `candidate` should be discarded instead of replacing a member of the population.
    
    In this example, we select a random member among the five worst in the population.
    """
    def replace(self, population, candidate):
        # population is a list of `Individual` objects
        # sort in order of fitness
        sorted_pop = sorted(population, key=lambda individual: individual.fitness)
        # choose one of the five members with worst fitness
        replacement = random.choice(sorted_pop[0:5])

        # find the index of the chosen member
        replacement_index = population.individuals.index(replacement)
        return replacement_index

    """ Step 11: You're done!  
    Go to the totter.evolution.__main__ file and import your new GA.  
    It should be available to run using the CLI:
    
    python -m totter evolve --algorithm ExampleGA
    """
