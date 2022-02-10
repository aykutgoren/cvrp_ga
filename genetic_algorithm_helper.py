# ----------------------------------------------------------------------------
# This module provides helper functions for Genetic Algorithm operations
#
# (C) Aykut Goren, 2022
# ----------------------------------------------------------------------------


import random


def create_random_vehicle_part(number_of_vehicle, sum_of_jobs):
    """
    Creates vehicle part of chromosome randomly.

    :param number_of_vehicle: Number of genes in chromosome.
    :param sum_of_jobs: Summation of number of jobs.
    """
    for i in range(number_of_vehicle):
        gene = random.randint(0, sum_of_jobs)
        if i == number_of_vehicle - 1:
            yield sum_of_jobs
        else:
            yield gene
            sum_of_jobs -= gene


def map_chromosome_to_routes(chromosome, number_of_jobs):
    """
    Maps chromosome to.

    :param chromosome: Individuals or solutions of algorithm.
    :param number_of_jobs: Number of jobs in chromosome.
    :return: Route list, which includes each list of each vehicle.
    """
    chromosome_vehicle_part = chromosome[number_of_jobs:]
    routes = []
    for vehicle in range(len(chromosome_vehicle_part)):
        start_gene = int(sum(chromosome_vehicle_part[:vehicle]))
        end_gene = int(start_gene + chromosome_vehicle_part[vehicle])
        routes.append(chromosome[start_gene:end_gene])
    return routes


def calculate_route_cost(route_locations, route, jobs, cost_matrix):
    """
    Calculates cost of each route.

    :param route_locations: Job locations indexes in route.
    :param route: Job ids in route.
    :param jobs: Jobs information, which includes job ids, location indexes and delivery.
    :param cost_matrix: Array of location to location travel cost.
    :return: Route cost including traveling cost and service cost
    """
    route_cost = 0
    for node in range(len(route_locations) - 1):
        traveling_cost = cost_matrix[route_locations[node]][route_locations[node + 1]]
        service_cost = jobs[route[node]][2]
        route_cost = route_cost + traveling_cost + service_cost
    return route_cost


def map_route_to_route_locations(vehicle_location, route, jobs):
    """
    Maps route list, which includes job ids to route location list.

    :param vehicle_location: Vehicle location index.
    :param route: Job ids in route.
    :param jobs: Jobs information, which includes job ids, location indexes and delivery.
    :return: Route location list including job location indexes.
    """
    route_locations = [vehicle_location]
    for job in route:
        job_location = jobs[job][0]
        route_locations.append(job_location)
    return route_locations


def map_chromosome_to_json_dictionary(chromosome, number_of_jobs, vehicles, cost_matrix, jobs):
    """
    Maps chromosome to the dictionary for json dump.

    :param chromosome: Individuals or solutions of algorithm.
    :param number_of_jobs: Number of jobs.
    :param vehicles: Vehicles information, which includes vehicle ids, start location indexes and capacities.
    :param cost_matrix: Array of location to location travel cost.
    :param jobs: Jobs information, which includes job ids, location indexes and delivery.
    :return: Dictionary for json dump.
    """
    routes = map_chromosome_to_routes(chromosome[0], number_of_jobs)
    routes = [list(route) for route in routes]  # Converted to list for json dump
    route_costs = []
    for route in routes:
        vehicle_id = list(vehicles)[routes.index(route)]  # Assuming
        vehicle_location = vehicles[vehicle_id][0]

        route_locations = map_route_to_route_locations(vehicle_location, route, jobs)
        route_costs.append(calculate_route_cost(route_locations, route, jobs, cost_matrix))
    # Merge route and route costs for dictionary
    route_and_cost_dictionary = zip(routes, route_costs)
    json_data_dictionary = {'total_delivery_duration': sum(route_costs),
                            'routes': {key: {'jobs': value[0], 'delivery_duration': value[1]} for key, value in
                                       zip(list(vehicles), list(route_and_cost_dictionary))}}
    return json_data_dictionary


def construct_offspring(parent1, parent_vehicle_part, parent2, parent2_vehicle_part, random_vehicle, number_of_jobs):
    """
    Constructs offspring.

    :param parent1: Parent 1 chromosome
    :param parent_vehicle_part: Vehicle part of parent 1
    :param parent2: Parent 2 chromosome
    :param parent2_vehicle_part: Vehicle part of parent 2
    :param random_vehicle: A random vehicle id
    :param number_of_jobs: Number of jobs.
    :return:
    """
    parent_vehicle_part_copy = parent_vehicle_part.copy()
    parent_vehicle_part_copy.pop(random_vehicle)
    offspring_vehicle_part = list(create_random_vehicle_part(len(parent_vehicle_part_copy),
                                                             number_of_jobs - parent2_vehicle_part[
                                                                 random_vehicle]))
    offspring_vehicle_part.insert(random_vehicle, parent2_vehicle_part[random_vehicle])
    start_gene = int(sum(parent2_vehicle_part[:random_vehicle]))
    end_gene = int(start_gene + parent2_vehicle_part[random_vehicle])
    offspring = [gene for gene in parent1[:number_of_jobs] if gene not in parent2[start_gene:end_gene]]
    for gene in parent2[start_gene:end_gene][::-1]:
        offspring.insert(start_gene, gene)
    offspring.extend(offspring_vehicle_part)
    return offspring
