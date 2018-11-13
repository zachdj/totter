from abc import abstractmethod
import math
import statistics


class TotterPopulation(object):
    @abstractmethod
    def replace(self, idx, replacement):
        pass

    @abstractmethod
    def best_fitness(self):
        pass

    @abstractmethod
    def mean_fitness(self):
        pass

    @abstractmethod
    def std_dev_fitness(self):
        pass

    @abstractmethod
    def __len__(self):
        pass


class Population(TotterPopulation):
    def __init__(self, individuals):
        """ Represents a set of totter.evolution.Individual objects.
        Automatically keeps track of the best individual.

        Args:
            individuals (Iterable<totter.evolution.Individual>):
                the Individuals in the initial population

        """
        self.size = len(individuals)
        self.individuals = individuals
        self.best_indv = self.individuals[0]
        for indv in self.individuals:
            if self.best_indv.fitness is None and indv.fitness is not None:
                self.best_indv = indv
            if indv.fitness is not None and indv.fitness > self.best_indv.fitness:
                self.best_indv = indv

    def replace(self, idx, replacement):
        """ Replace the individual at `idx` with `replacement` """
        if idx >= self.size:
            raise IndexError

        self.individuals[idx] = replacement
        if replacement.fitness > self.best_indv.fitness:
            self.best_indv = replacement

    def best_fitness(self):
        return self.best_indv.fitness

    def mean_fitness(self):
        fitness_vals = list(map(lambda i: i.fitness, self.individuals))
        return statistics.mean(fitness_vals)

    def std_dev_fitness(self):
        fitness_vals = list(map(lambda i: i.fitness, self.individuals))
        return statistics.stdev(fitness_vals)

    def to_grid(self):
        return GriddedPopulation(self.individuals)

    def __getitem__(self, idx):
        if idx >= self.size:
            raise IndexError

        return self.individuals[idx]

    def __len__(self):
        return self.size


class GriddedPopulation(Population):
    def __init__(self, individuals):
        """ Represents a population organized along a grid """
        super().__init__(individuals)
        self.rows = int(math.floor(math.sqrt(self.size)))
        self.cols = int(math.ceil(math.sqrt(self.size)))
        # ensure population can be made into a grid:
        if self.rows * self.cols != self.size:
            raise ValueError('Population cannot be made into a grid.  Aborting.')

    def wrap_coords(self, row, col):
        """ Takes row, col coordinates and wraps them so that they are in bounds of the grid
        
        Indices larger than the grid will wrap around to the beginning.  Negative indices will wrap around to the end.
        
        Args:
            row (int): index of the row to access 
            col (int): index of the col to access 

        Returns:
            int, int: row within bounds, col within bounds

        """
        wrapped_row, wrapped_col = row, col
        # wrap negatives around to count backwards from the end of the array
        while wrapped_row < 0:
            wrapped_row = self.rows + wrapped_row
        while wrapped_col < 0:
            wrapped_col = self.cols + wrapped_col

        # wrap indices greater than the limits around to the beginning
        wrapped_row = wrapped_row % self.rows
        wrapped_col = wrapped_col % self.cols

        return wrapped_row, wrapped_col

    def coords_to_index(self, row, col):
        """ Converts (row, col) coordinates to coordinates along the linear array

        Args:
            row (int): index of the row in grid-space
            col (int): index of the column in grid-space

        Returns:
            int: index in linear space

        """
        return self.cols * row + col

    def get_by_coords(self, row, col):
        wrapped_row, wrapped_col = self.wrap_coords(row, col)
        idx = self.coords_to_index(wrapped_row, wrapped_col)
        return self.individuals[idx]

    def replace_by_coords(self, row, col, replacement):
        wrapped_row, wrapped_col = self.wrap_coords(row, col)
        idx = self.coords_to_index(wrapped_row, wrapped_col)
        self.replace(idx, replacement)
