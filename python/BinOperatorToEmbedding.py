import json
import math
import sys
import time
import glob

from os import getcwd
from os.path import join

import Util

def parse_data_paths(args):
    paths = []
    for arg in args:
        for bin_op_file in glob.glob(join(getcwd(), arg)):
            paths.append(bin_op_file)
    return paths


def scan_ops(data_paths):
    all_operators_set = set()
    data_paths = parse_data_paths(data_paths)
    for bin_op in Util.DataReader(data_paths):
        if bin_op["op"] not in all_operators_set:
            all_operators_set.add(bin_op["op"])
    all_operators = list(all_operators_set)
    return all_operators


def create_op_embeddings(all_operators):
    embeddings = {}
    for i, operator in enumerate(all_operators):
        embeddings[operator] = [0] * len(all_operators)
        embeddings[operator][i] = 1
    return embeddings


if __name__ == '__main__':
    # arguments: <binOp data files>
    data_paths = sys.argv[1:]
    all_ops = scan_ops(data_paths)
    embeddings = create_op_embeddings(all_ops)
    time_stamp = math.floor(time.time() * 1000)
    operator_to_vector_file = "operator_to_vector_" + str(time_stamp) + ".json"
    with open(join(getcwd(), operator_to_vector_file), "w") as file:
        json.dump(embeddings, file, sort_keys=True, indent=4)