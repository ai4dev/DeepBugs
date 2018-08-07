'''
Created on 06.08.18

@author: Egor Bogomolov
'''


import ast
from ast import Attribute, Name
from ExtractorUtils import identifier_string, get_name_of_ast_node



class FunctionDefinitionCollector(ast.NodeVisitor):

    def __init__(self, function_to_parameters):
        self.function_to_parameters = function_to_parameters

    def visit_FunctionDef(self, node):
        print("I've visited function {}".format(node.name))
        name = identifier_string.format(node.name)
        if name not in self.function_to_parameters and len(node.args.args) > 1:
            args = []
            for arg in node.args.args:
                args.append(identifier_string.format(arg.arg))
            self.function_to_parameters[name] = args
        self.generic_visit(node)


class CallsCollector(ast.NodeVisitor):

    def __init__(self, function_to_parameters):
        self.function_to_parameters = function_to_parameters

    def visit_Call(self, node):
        if len(node.args) > 1:
            print('---------------')

            base = ""
            callee_node = node.func
            callee = get_name_of_ast_node(callee_node)
            if type(callee_node) is Attribute:
                base = get_name_of_ast_node(callee_node.value)
            elif type(callee_node) is not Name:
                print("ERROR! ERROR!")
            print("base:", base)
            print("callee:", callee)
            print('---------------')
        self.generic_visit(node)


def extract_calls(file, resulting_json):
    with open(file) as fin:
        tree = ast.parse(fin.read(), file)
        function_to_parameters = {}
        FunctionDefinitionCollector(function_to_parameters).visit(tree)
        CallsCollector(function_to_parameters).visit(tree)
