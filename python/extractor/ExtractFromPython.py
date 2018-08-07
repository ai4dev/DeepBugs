"""
Created on 31.07.18

@author: Egor Bogomolov
"""

import argparse
import os
import json
import time
import ExtractorUtils as utils
from ExtractorOfCalls import extract_calls

usage = """
Correct usage:

python3 ExtractFromPython.py <what> <prefix> <fileList.txt> <dir>

    Analyze all files in <dir> that are listed in <fileList.txt>.
    If <fileList.txt> is "all", analyze all files in <dir>.

    The <what> argument must be one of:
        tokens
        calls
        callsMissingArg
        assignments
        binOps
        idsLitsWithTokens
        idsLitsWithIds
        idsLitsWithASTFamily
"""


def invalid_usage(error):
    if error:
        print()
        print(error)
    print(usage)
    exit(1)


supported_targets = ["tokens", "calls", "assignments", "callsMissingArg", "binOps", "idsLitsWithTokens",
                     "idsLitsWithIds", "idsLitsWithASTFamily"]

root_global = os.getcwd()
tech_files_dir = os.path.join(root_global, "data/tech/")
file_to_id_filename = os.path.join(tech_files_dir, "fileIDs.json")
tech_file_template = '{}_{}_{}.json'


def get_file_from_template(what, prefix):
    return os.path.join(tech_files_dir, tech_file_template.format(what, prefix, int(time.time())))


def get_file_to_id(files):
    file_to_id = {}
    if os.path.isfile(file_to_id_filename):
        with open(file_to_id_filename) as fin:
            file_to_id = json.load(fin)
    max_id = 1
    for file in file_to_id:
        max_id = max(max_id, file_to_id[file])
    added = False
    for file in files:
        if file not in file_to_id:
            max_id += 1
            file_to_id[file] = max_id
            added = True

    if added:
        with open(file_to_id_filename, 'w') as fout:
            json.dump(file_to_id, fout, indent=4, separators=(',', ': '))

    return file_to_id


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('target', help='extracted information, one of: \'calls\'')
    parser.add_argument('prefix', help='prefix appended to all generated files')
    parser.add_argument('files', help='list of files to include')
    parser.add_argument('path_to_files', help='directory that is recursively scanned for files')
    args = parser.parse_args()

    if args.target not in supported_targets:
        invalid_usage("{} is not in supported tokens".format(args.target))

    root_data = os.path.join(root_global, args.path_to_files)
    python_files = []
    for root, directories, filenames in os.walk(root_data):
        for filename in filenames:
            if filename.endswith(".py") and filename != "__init__.py":
                python_files.append(os.path.join(root, filename))
    print("Collected {} .py files".format(len(python_files)))

    if args.files != "all":
        with open(args.files) as fin:
            files_to_consider = set(map(lambda fname: os.path.join(root_global, fname), fin.read().splitlines()))
            python_files = list(filter(lambda fname: fname in files_to_consider, python_files))
            print("{} files left".format(len(python_files)))

    file_to_id = get_file_to_id(python_files)
    resulting_json = []

    for file in python_files:
        # resulting_json.append({'path': file, 'tokens': utils.get_tokens(file)})
        if args.target == 'tokens':
            utils.get_tokens(file, resulting_json)
        elif args.target == 'calls':
            extract_calls(file, resulting_json)


    with open(get_file_from_template(args.target, args.prefix), 'w') as fout:
        json.dump(resulting_json, fout, indent=4, separators=(',', ': '))
