'''
Created on 06.08.18

@author: Egor Bogomolov
'''


import ast
from ast import Attribute, Name, Subscript
from ExtractorUtils import identifier_string, get_name_of_ast_node, get_location_of_ast_node, get_type_of_ast_node, get_base_of_ast_node
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
                args.append(identifier_string.format(arg.arg))
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
            parameter = ''
            if callee in self.function_to_parameters and i < len(self.function_to_parameters[callee]):
                parameter = self.function_to_parameters[callee][i]
            parameters.append(parameter)

        callee = callee[:min(max_length_of_callee_and_args, len(callee))]
        base = base[:min(max_length_of_callee_and_args, len(base))]
        location = self.path + " : " + str(node.first_token.start[0]) + " - " + str(node.last_token.end[0])
        self.calls.append({
            'base':base,
            'callee':callee,
            'calleeLocation':callee_location,
            'arguments':arg_strings,
            'argumentLocations':arg_locations,
            'argumentTypes':arg_types,
            'parameters':parameters,
            'src':location,
            'filename':self.path
        })

        self.generic_visit(node)


def extract_calls(file, file_id, resulting_json):
    print("Extracting from {}".format(file))
    with open(file) as fin:
        try:
            atok = asttokens.ASTTokens(fin.read(), parse=True, filename=file)
        except SyntaxError:
            print("Unable to extract from {}, incompatible python version".format(file))
            return
        except ValueError:
            print("Unable to extract from {}, failed to extract tokens".format(file))
            return
        except TokenError:
            print("Unable to extract from {}, failed with tokenizing".format(file))
            return
        tree = atok.tree
        function_to_parameters = {}
        FunctionDefinitionCollector(function_to_parameters).visit(tree)
        CallsCollector(function_to_parameters, file_id, file, resulting_json).visit(tree)
