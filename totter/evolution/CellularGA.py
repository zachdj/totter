""" Cellular Genetic Algorithm

Organizes populations across a grid and restricts crossover to the fittest neighbor.
Note that this GA ignores the `cx_prob` and the `generational` parameters.  Crossover is always performed and the GA is
also elitist generational.

"""

import math

from totter.evolution.GeneticAlgorithm import GeneticAlgorithm, Individual
from totter.utils.time import WallTimer


class CellularGA(GeneticAlgorithm):
    def __init__(self,
                 evaluations=2000,
                 eval_time_limit=600,
                 pop_size=30,
                 cx_prob=0.9,
                 mt_prob=0.05,
                 steady_state=True,
                 seed_population=False,
                 random_seed=1234):

        super().__init__(evaluations, eval_time_limit, pop_size, cx_prob, mt_prob, steady_state, seed_population, random_seed)
        self.rows = int(math.floor(math.sqrt(self.pop_size)))
        self.cols = int(math.ceil(math.sqrt(self.pop_size)))
        # ensure population can be made into a grid:
        if self.rows * self.cols != self.pop_size:
            raise ValueError('Population cannot be made into a grid.  Aborting.')
        self.grid_population()

    def grid_population(self):
        population_grid = [self.population[i * self.cols:(i + 1) * self.cols] for i in range(0, self.rows)]
        self.population = population_grid

    def seed(self, pool_size, time_limit=60):
        super().seed(pool_size, time_limit)
        self.grid_population()

    def run(self):
        # ensure population has been evaluated and best_indv is up-to-date
        # this is necesary after a GA is constructed or after loading a GA from disk
        for indv in self.population:
            if indv.fitness is None:
                self._evaluate(indv)
            if self.best_indv.fitness is None or indv.fitness > self.best_indv.fitness:
                self.best_indv = indv

        # time the run
        timer = WallTimer()
        while self.total_evaluations < self.max_evaluations:
            # iterate over population
            for row in range(0, self.rows):
                for col in range(0, self.cols):
                    parent1 = self.population[row][col]
                    # select the fittest neighbor as parent 2
                    left_neighbor = self.population[row][col-1]
                    parent2 = left_neighbor
                    right_neighbor = self.population[row][(col+1) % self.cols]
                    if right_neighbor.fitness > parent2.fitness:
                        parent2 = right_neighbor
                    top_neighbor = self.population[row-1][col]
                    if top_neighbor.fitness > parent2.fitness:
                        parent2 = top_neighbor
                    bottom_neighbor = self.population[(row+1) % self.rows][col]
                    if bottom_neighbor.fitness > parent2.fitness:
                        parent2 = bottom_neighbor

                    # produce a child
                    child_genome = self.crossover(parent1.genome, parent2.genome)[0]
                    # mutate the child
                    if self.mt_prob < child_genome:
                        child_genome = self.mutate(child_genome)

                    child_genome = self.repair(child_genome)
                    child = Individual(genome=child_genome)
                    self._evaluate(child)

                    # replace current cell if better
                    if child.fitness > parent1.fitness:
                        self.population[row][col] = child

                    # update best individual the GA has found so far
                    if self.best_indv is None or child.fitness > self.best_indv.fitness:
                        self.best_indv = child

            # record history
            if self.best_indv is not None:
                best_fitness = self.best_indv.fitness
                average_fitness = sum(map(lambda indv: indv.fitness, self.population)) / len(self.population)
                self.history.append([self.generations, best_fitness, average_fitness])

            self.generations += 1

        return timer.since()
