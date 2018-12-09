'''
Created on 06.08.18

@author: Egor Bogomolov
'''


import ast
from ExtractorUtils import identifier_string, get_name_of_ast_node, get_location_of_ast_node, get_type_of_ast_node, get_base_of_ast_node,\
    try_to_extract, literal_string
import asttokens
from tokenize import TokenError


max_length_of_callee_and_args = 200


class FunctionDefinitionCollector(ast.NodeVisitor):

    def __init__(self, function_to_parameters):
        self.function_to_parameters = function_to_parameters

    def visit_FunctionDef(self, node):
        name = identifier_string.format(node.name)
        if name not in self.function_to_parameters and len(node.args.args) > 1:
            args = []
            for arg in node.args.args:
                arg_name = get_name_of_ast_node(arg)
                if arg_name is None:
                    self.generic_visit(node)
                    return
                args.append(arg_name)
            if args[0] == identifier_string.format("self") and "ID:_" not in name:
                args.pop(0)
            self.function_to_parameters[name] = args
        self.generic_visit(node)


class CallsCollector(ast.NodeVisitor):

    def __init__(self, function_to_parameters, file_id, path, calls):
        self.function_to_parameters = function_to_parameters
        self.file_id = str(file_id)
        self.path = path
        self.calls = calls

    def visit_Call(self, node):
        if len(node.args) <= 1:
            self.generic_visit(node)
            return

        base = ""
        callee_node = node.func
        callee = get_name_of_ast_node(callee_node)
        base = get_base_of_ast_node(callee_node)
        if base is None or callee is None:
            self.generic_visit(node)
            return

        callee_location = self.file_id + get_location_of_ast_node(callee_node)

        arg_strings = []
        arg_locations = []
        arg_types = []
        parameters = []

        for i, arg in enumerate(node.args):
            arg_name = get_name_of_ast_node(arg)
            if arg_name is None:
                self.generic_visit(node)
                return
            arg_strings.append(arg_name[:min(max_length_of_callee_and_args, len(arg_name))])
            arg_locations.append(self.file_id + get_location_of_ast_node(arg))
            arg_types.append(get_type_of_ast_node(arg))
            if arg_strings[-1] in [identifier_string.format("self"), literal_string.format("self")]:
                arg_types[-1] = "object"
            parameter = ''
            if callee in self.function_to_parameters and i < len(self.function_to_parameters[callee]):
                parameter = self.function_to_parameters[callee][i]
            parameters.append(parameter)

        callee = callee[:min(max_length_of_callee_and_args, len(callee))]
        base = base[:min(max_length_of_callee_and_args, len(base))]
        location = self.path + " : " + str(node.first_token.start[0]) + " - " + str(node.last_token.end[0])
        self.calls.append({
            'base': base,
            'callee': callee,
            'calleeLocation': callee_location,
            'arguments': arg_strings,
            'argumentLocations': arg_locations,
            'argumentTypes': arg_types,
            'parameters': parameters,
            'src': location,
            'filename': self.path
        })

        self.generic_visit(node)



def extract_calls(project_files, file_ids, resulting_json):

    function_to_parameters = {}
    for i, file in enumerate(project_files):
        #with open(file) as fin:
        print("Extracting functions from {}".format(file))
        tree = try_to_extract(file)
        if tree is None:
            continue
        FunctionDefinitionCollector(function_to_parameters).visit(tree)
    for i, file in enumerate(project_files):
        #with open(file) as fin:
        print("Extracting calls from {}".format(file))
        tree = try_to_extract(file)
        if tree is None:
            continue
        CallsCollector(function_to_parameters, file_ids[file], file, resulting_json).visit(tree)
