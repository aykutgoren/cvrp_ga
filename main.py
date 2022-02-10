# ----------------------------------------------------------------------------
# This module runs Genetic Algorithm for CVRP if input json file is valid.
#
# (C) Aykut Goren, 2022
# ----------------------------------------------------------------------------


from genetic_algorithm import GeneticAlgorithm
from json_parser import JsonParser

if __name__ == '__main__':
    input_file_name = 'input.json'
    # If input file is valid, run program
    if JsonParser.is_valid(input_file_name):
        # Parse json input file
        input_data = JsonParser.get_json_data(input_file_name)
        # Create a genetic algorithm object by initializing with input data
        genetic_algorithm = GeneticAlgorithm(input_data)
        # Run Genetic Algorithm
        genetic_algorithm.run()
