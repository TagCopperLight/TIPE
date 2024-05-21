import random
import matplotlib.pyplot as plt
from multiprocessing import Pool
from itertools import product
from math import prod, exp
from methods.get_tree import create_decision_tree_files, create_decision_tree_from_dict


class Individual:
    def __init__(self, features):
        self.features = features
        self.int_length = prod([len(feature) for feature in self.features])

        self.individual = 0

        for _ in range(1):
            self.individual ^= 1 << random.randint(0, self.int_length - 1)

        self.fitness = 0

    # def __repr__(self):
        # return f'{self.individual:0>{self.int_length}b}'

class Population:
    def __init__(self, size, features):
        self.size = size
        self.features = features
        self.population = [Individual(features) for _ in range(self.size)]
        
    def __repr__(self):
        r = "["
        for individual in self.population:
            r += f'{individual.fitness}, '
        r = r[:-2] + "]"
        return r

class GeneticAlgorithm:
    def __init__(self, games, population_size, features):
        self.games = games
        self.features = features
        self.population_size = population_size
        self.propagation_rate = 0.8
        self.crossover_rate = 0.8
        self.mutation_rate = 0.0005

        self.population = Population(self.population_size, self.features)

    def get_features(self, individual, selected_features_index=[], selected_features=[]):
        if len(selected_features_index) == len(self.features):
            shift = 0
            for index, s_feature in enumerate(reversed(selected_features_index)):
                reversed_index = len(selected_features_index) - index - 1
                fixed_features = self.features + [[0]]
                last_lengths = [len(feature) for feature in fixed_features[reversed_index+1:]]
                shift += s_feature * prod(last_lengths)

            if individual.individual & (1 << shift):
                return selected_features
            
            return None
        
        features = []

        for index, _ in enumerate(self.features[len(selected_features_index)]):
            value = self.get_features(individual, selected_features_index + [index], selected_features + [self.features[len(selected_features_index)][index]])
            if value and type(value[0]) != list:
                features.append(value)
            elif value:
                features += value

        return features
    
    def set_features(self, features):
        int = 0

        reversed_features = [reversed(feature) for feature in self.features]

        for i in product(*reversed_features):
            if list(i) in features:
                int = (int << 1) | 1
            else:
                int = int << 1

        return int

    def threaded_fitness(self, args):
        id = args[0]
        print(f'Process {id} started')
        args = args[1]
        computed_values = {}
        for i, individual in args:
            if (i+1) % 100 == 0:
                print(f'{i+1}/{self.population_size}')
            raw_features = self.get_features(individual)
            features = []
            for feature in raw_features:
                if feature[1] == 10:
                    features.append((feature[0], f'DEATH', feature[2]))
                else:
                    player = ['T1-R1', 'T1-R2', 'T1-R3', 'T1-R4', 'T1-R5', 'T2-R1', 'T2-R2', 'T2-R3', 'T2-R4', 'T2-R5'][feature[1]]
                    features.append((feature[0], player, feature[2]))

            names, data = create_decision_tree_files(self.games, features, False)
            tree = create_decision_tree_from_dict(names, data)
            accuracy = tree.get_accuracy() - accuracy_fix(features)
            computed_values[individual] = (id, i, accuracy)

        return computed_values

    def fitness(self, processes=24):
        args = list(enumerate(self.population.population))

        with Pool(processes=processes) as pool:
            results = pool.map(self.threaded_fitness, [(i, chunk) for i, chunk in enumerate(chunk_split(args, processes))], chunksize=1)
            pool.close()

        args = [(i, chunk) for i, chunk in enumerate(chunk_split(args, processes))]
        for result in results:
            for _, accuracy in result.items():
                for i, individual in args[accuracy[0]][1]:
                    if i == accuracy[1]:
                        individual.fitness = accuracy[2]
                        break

    def rank_selection(self):
        ranked_population = sorted(self.population.population, key=lambda ind: ind.fitness, reverse=True)[2:]
        selection_probabilities = list(reversed([i / len(ranked_population) for i in range(1, len(ranked_population) + 1)]))

        selected = random.choices(ranked_population, weights=selection_probabilities, k=round(len(ranked_population)*self.propagation_rate))

        return selected
    
    def crossover(self, parent1, parent2):
        child1 = Individual(self.features)
        child2 = Individual(self.features)

        point1, point2 = random.randint(0, child1.int_length - 1), random.randint(0, child1.int_length - 1)
        if point1 > point2:
            point1, point2 = point2, point1

        outer_mask = ((1 << point1) - 1) << (parent1.int_length - point1) | ((1 << (parent1.int_length - point2)) - 1)
        inner_mask = ((1 << point2 - point1) - 1) << (parent1.int_length - point2)

        if random.random() < self.crossover_rate:
            child1.individual = (parent1.individual & outer_mask) | (parent2.individual & inner_mask)
            child2.individual = (parent2.individual & outer_mask) | (parent1.individual & inner_mask)
        else:
            child1.individual = parent1.individual
            child2.individual = parent2.individual

        return child1, child2
    
    def mutation(self, children):
        for child in children:
            for i in range(child.int_length):
                if random.random() < self.mutation_rate:
                    child.individual ^= 1 << i
        return children
    
    def next_generation(self):
        self.fitness()

        max_ind = max(self.population.population, key=lambda ind: ind.fitness)
        max_features = self.get_features(max_ind)
        max_fitness = max_ind.fitness
        true_max_fitness = max_fitness + accuracy_fix(max_features)
        min_fitness = min(self.population.population, key=lambda ind: ind.fitness).fitness
        avg_fitness = sum([ind.fitness for ind in self.population.population]) / len(self.population.population)
        print(f'Max: {max_fitness}, Min: {min_fitness}, Avg: {avg_fitness}, True Max: {true_max_fitness}')
        print(f'Max features: {self.get_features(max(self.population.population, key=lambda ind: ind.fitness))}')

        selected = self.rank_selection()

        ranked_population = sorted(self.population.population, key=lambda ind: ind.fitness, reverse=True)
        new_population = [ranked_population[0], ranked_population[1]]
        while len(new_population) < self.population_size:
            children = self.crossover(random.choice(selected), random.choice(selected))
            children = self.mutation(children)
            new_population += children
        
        self.population.population = new_population

        return max_fitness, min_fitness, avg_fitness, true_max_fitness     
    

def main(games):
    pop_size = 1000
    genetic_algorithm = GeneticAlgorithm(games, pop_size, [['indeg', 'outdeg', 'cls', 'btw', 'eige'], list(range(11)), list(range(30))])
    # i = genetic_algorithm.set_features([['outdeg', 0, 12], ['outdeg', 4, 11], ['cls', 8, 2], ['btw', 9, 8], ['eige', 10, 9]])
    # genetic_algorithm.population.population[0].individual = i

    maxes = []
    avgs = []
    true_maxes = []
    for i in range(200):
        print(f'Generation {i+1}')
        ma, mi, av, tma = genetic_algorithm.next_generation()
        maxes.append(ma)
        avgs.append(av)
        true_maxes.append(tma)

    plt.plot(maxes, label='Max')
    plt.plot(avgs, label='Avg')
    plt.plot(true_maxes, label='True Max')

    plt.show()

if __name__ == '__main__':
    main()