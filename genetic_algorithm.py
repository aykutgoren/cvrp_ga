# ----------------------------------------------------------------------------
# This module includes Genetic Algorithm class for CVRP.
# Chromosome representation is composed of 2 parts. First part is job part, which includes
# job ids in genes and second part is vehicle part, which includes vehicles by gene order.
#
# Example:
# chromosome -> 1324567322
# job part -> 1324567
# vehicle part -> 322
# First vehicle route -> 132
# Second vehicle route -> 45
# Third vehicle route -> 67
#
#           Genetic Algorithm process:
#
# 1. Initialize population
# 2. Fitness calculation
# 3. Selection
# 4. Crossover
# 5. Mutation
# 6. Update Population
# 7. Check termination criteria

# Generation number is the only termination criteria.
#
# (C) Aykut Goren, 2022
# ----------------------------------------------------------------------------


import numpy as np

from genetic_algorithm_helper import *
from json_parser import JsonParser


class GeneticAlgorithm:
    def __init__(self, data):
        """
        The constructor for GeneticAlgorithm class.

        :param data: Input data, which is parsed by JsonParser class.
        """
        # Input parameters from json file.
        self.data = data
        self.vehicles = {d['id']: [d['start_index'], d['capacity'][0]] for d in data['vehicles']}
        self.jobs = {d['id']: [d['location_index'], d['delivery'][0], d['service']] for d in data['jobs']}
        self.matrix = [item for item in self.data['matrix']]
        self.number_of_vehicles = len(self.vehicles)
        self.number_of_jobs = len(self.jobs)

        # Genetic Algorithm parameters
        self.generations = 100
        self.chromosomes = 10
        self.mating_pool_size = 6  # Must be greater than half of chromosomes
        self.genes = self.number_of_vehicles + self.number_of_jobs
        self.offspring_size = self.chromosomes - self.mating_pool_size
        self.population = np.empty((self.chromosomes, self.genes), dtype='int')
        self.fitness = 0

        # Create initial population
        self.__initial_population()

    def __initial_population(self):
        """
        Creates initial population.
        """
        job_ids = list(self.jobs.keys())
        chromosome_job_part = [random.sample(job_ids, self.number_of_jobs) for i in
                               range(self.chromosomes)]
        self.population[:, :self.number_of_jobs] = np.array(chromosome_job_part)
        chromosome_vehicle_part = []
        for _ in self.population:
            random_vehicle_part = list(create_random_vehicle_part(self.number_of_vehicles, self.number_of_jobs))
            chromosome_vehicle_part.append(random_vehicle_part)
        self.population[:, self.number_of_jobs:] = chromosome_vehicle_part

    def __fitness(self, chromosomes):
        """
        Calculates fitness of given chromosomes.

        :param chromosomes: Individuals or solutions of algorithm.
        :return: Total cost value.
        """
        self.total_cost = []
        for chromosome in chromosomes:
            routes = map_chromosome_to_routes(chromosome, self.number_of_jobs)
            chromosome_cost = 0
            for i in range(self.number_of_vehicles):
                route_cost = 0
                if chromosome[len(self.jobs) + i] > 0:
                    vehicle_id = list(self.vehicles)[i] # Vehicle ids are mapped to chromosome vehicle part in order
                    vehicle_location = self.vehicles[vehicle_id][0]
                    route_locations = map_route_to_route_locations(vehicle_location, routes[i], self.jobs)
                    route_cost = calculate_route_cost(route_locations, routes[i], self.jobs, self.matrix)
                    penalty = self.__penalty(vehicle_id, routes[i])
                    route_cost += penalty * route_cost
                chromosome_cost = chromosome_cost + route_cost
            self.total_cost.append(chromosome_cost)
        return self.total_cost

    def __penalty(self, vehicle_id, route):
        """
        Calculates penalty of given route. If route violates capacity constraint, penalty score added to cost.

        :param vehicle_id: Vehicle ID
        :param route: Locations, which will be visited by the vehicle.
        :return: Penalty score.
        """
        penalty = 0
        vehicle_capacity = self.vehicles[vehicle_id][1]
        route_total_delivery = 0
        for job in route:
            job_delivery = self.jobs[job][1]
            route_total_delivery += job_delivery
            if route_total_delivery > vehicle_capacity:
                penalty += 1000
        return penalty

    def __print(self):
        """
        Prints a report for each iteration.
        """
        print("Generation: ", self.generation + 1, "\nPopulation\n", self.population, "\nFitness\n",
              self.fitness, '\n')

    def __selection(self):
        """
        Selects best parents for next generation.
        """
        self.parents = [chromosome for _, chromosome in sorted(zip(self.fitness, self.population), key=lambda x: x[0])]
        self.parents = self.parents[:self.mating_pool_size]

    def __crossover(self):
        """
        Creates offspring from parents in mating pool.
        Ordered Crossover procedure is applied.
        """
        self.offspring = np.empty((self.offspring_size, self.genes), dtype='int')
        for i in range(0, self.offspring_size):
            # offspring1 vehicle part
            parent1 = list(self.parents[i])
            parent2 = list(self.parents[i + 1])
            parent1_vehicle_part = parent1[self.number_of_jobs:]
            parent2_vehicle_part = parent2[self.number_of_jobs:]
            random_vehicle = random.randint(0, self.number_of_vehicles - 1)
            self.offspring[i, :] = construct_offspring(parent1, parent1_vehicle_part, parent2,
                                                       parent2_vehicle_part,
                                                       random_vehicle, self.number_of_jobs)

    def __mutation(self):
        """
        Mutates offspring.
        An adaptive mutation procedure is applied. If the fitness of the offspring is greater than the
        average fitness of the population, it is called low-quality solution and the mutation probability will be
        high and vice versa.

        """
        average_fitness = np.average(self.fitness)
        for i in range(self.offspring_size):
            fitness = self.__fitness([self.offspring[i]])
            if fitness >= average_fitness:
                # Low-quality solution
                mutation_rate = 0.9
            else:
                # High-quality solution
                mutation_rate = 0.1
            if random.random() > mutation_rate:
                random_vehicle = random.randint(0, self.number_of_vehicles - 1)
                random_vehicle_index = self.number_of_jobs + random_vehicle
                # If the route has more than 1 location for service, swap 2 service locations randomly inside the route,
                # otherwise swap 2 random service locations in offspring regardless of routes of vehicles.
                # This condition prioritize the mutation in route to sustain the parent gene transfer stability.
                if self.offspring[i][random_vehicle_index] > 1:
                    start_gene = int(sum(self.offspring[i][self.number_of_jobs:random_vehicle_index]))
                    end_gene = int(start_gene + self.offspring[i][random_vehicle_index])
                else:
                    start_gene = 0
                    end_gene = self.number_of_jobs
                mutation_points = random.sample(range(start_gene, end_gene), 2)
                for point in range(len(mutation_points) - 1):
                    self.offspring[i][mutation_points[point]], self.offspring[i][mutation_points[point + 1]] = \
                        self.offspring[i][mutation_points[point + 1]], self.offspring[i][mutation_points[point]]

    def run(self):
        """
        Runs Genetic Algorithm loop:
        1. Selection
        2. Crossover
        3. Mutation
        """
        for self.generation in range(self.generations):
            self.fitness = self.__fitness(self.population)
            self.__print()
            self.__selection()
            self.__crossover()
            self.__mutation()
            self.population[:len(self.parents), :] = self.parents
            self.population[len(self.parents):, :] = self.offspring

        best_solution = [self.population[0]]
        json_data = map_chromosome_to_json_dictionary(best_solution, self.number_of_jobs, self.vehicles, self.matrix,
                                                      self.jobs)
        JsonParser.write_json_data(json_data)
