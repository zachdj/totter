import copy


class Individual:
    """ Represents an individual with a genome and a fitness value """
    def __init__(self, genome):
        self.genome = genome
        self.fitness = None

    def clone(self):
        cloned_self = Individual(copy.deepcopy(self.genome))
        cloned_self.fitness = self.fitness
        return cloned_self

    def __str__(self):
        return f'Individual: {self.genome}\tFitness: {self.fitness}'

    def __len__(self):
        return len(self.genome)
