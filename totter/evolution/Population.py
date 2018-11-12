class Population(object):
    def __init__(self, individuals):
        """ Represents a set of totter.evolution.Individual objects.
        Automatically keeps track of the best individual.

        Args:
            individuals (Iterable<totter.evolution.Individual>):
                the Individuals in the initial population

        """
        self.size = len(individuals)
        self.pop = individuals
        self.best_indv = self.pop[0]
        for indv in self.pop:
            if self.best_indv.fitness is None and indv.fitness is not None:
                self.best_indv = indv
            if indv.fitness is not None and indv.fitness > self.best_indv.fitness:
                self.best_indv = indv

    def get(self, idx):
        if idx >= self.size:
            raise IndexError

        return self.pop[idx]

    def replace(self, idx, replacement):
        """ Replace the individual at `idx` with `replacement` """
        if idx >= self.size:
            raise IndexError

        self.pop[idx] = replacement
        if replacement.fitness > self.best_indv.fitness:
            self.best_indv = replacement

    def __getitem__(self, idx):
        return self.get(idx)

    def __len__(self):
        return self.size


def seed(pool_size, time_limit, evaluator):
    """ Construct a population by seeding it with the best runners from a pool of randomly-generated runners

    Args:
        pool_size:
        time_limit:
        evaluator:

    Returns:

    """