# ----------------------------------------------------------------------------
# This module includes JsonParser class, which has static methods to check,
# read and write Json file.
#
# (C) Aykut Goren, 2022
# ----------------------------------------------------------------------------


import json

import numpy as np


def np_encoder(_object):
    """
    Numpy encoder for json dump.

    """
    if isinstance(_object, np.generic):
        return _object.item()


class JsonParser:
    # noinspection PyUnusedLocal
    @staticmethod
    def is_valid(input_file):
        """
        Checks if input file is valid.
        :param input_file: Input Json file
        :return: Boolean
        """
        try:
            with open(input_file, 'r') as file:
                data = json.load(file)
            # Try parsing the json file
            vehicles = {d['id']: [d['start_index'], d['capacity'][0]] for d in data['vehicles']}
            jobs = {d['id']: [d['location_index'], d['delivery'][0], d['service']] for d in data['jobs']}
            matrix = [item for item in data['matrix']]
            return True
        except ValueError as e:
            print("Error: ", e)
            return False
        except Exception as e:
            print("Error: Input json file format is not correct ! Exception:", e)
            return False

    @staticmethod
    def get_json_data(input_file):
        """
        Reads json file.

        :param input_file: Json file name.
        :return: Dictionary
        """
        with open(input_file, 'r') as file:
            data = json.load(file)
            return data

    @staticmethod
    def write_json_data(json_data):
        """
        Writes json file.

        :param json_data: Dictionary
        """
        with open('output.json', 'w') as file:
            json.dump(json_data, file, indent=4, default=np_encoder)
