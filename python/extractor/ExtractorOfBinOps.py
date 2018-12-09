'''
Created on 29.08.18

@author: Egor Bogomolov
'''

import ast
from ExtractorUtils import get_name_of_ast_node, get_location_of_ast_node, get_type_of_ast_node, get_operation_token, try_to_extract
import asttokens
from tokenize import TokenError

class BinOpsCollector(ast.NodeVisitor):

    def __init__(self, function_to_parameters, file_id, path, bin_ops):
        self.function_to_parameters = function_to_parameters
        self.file_id = str(file_id)
        self.path = path
        self.bin_ops = bin_ops

    def collect_bin_op(self, node, left, op, right):
        left_name = get_name_of_ast_node(left)
        right_name = get_name_of_ast_node(right)
        left_type = get_type_of_ast_node(left)
        right_type = get_type_of_ast_node(right)
        parent_type = type(node.parent)
        grand_parent_type = '' \
            if node.parent is None or node.parent.parent is None \
            else type(node.parent.parent)

        if left_name is not None and right_name is not None:
            location = self.path + " : " + str(node.first_token.start[0]) + " - " + str(node.last_token.end[0])
            self.bin_ops.append({
                'left': left_name,
                'right': right_name,
                'op': get_operation_token(op),
                'leftType': left_type,
                'rightType': right_type,
                'parent': parent_type.__name__,
                'grandParent': grand_parent_type.__name__,
                'src': location
            })

    def visit_BinOp(self, node):
        self.collect_bin_op(node, node.left, node.op, node.right)
        self.generic_visit(node)

    def visit_BoolOp(self, node):
        if len(node.values) != 2:
            self.generic_visit(node)
            return
        self.collect_bin_op(node, node.values[0], node.op, node.values[1])
        self.generic_visit(node)

    def visit_Compare(self, node):
        if len(node.ops) == 1:
            self.collect_bin_op(node, node.left, node.ops[0], node.comparators[0])
        self.generic_visit(node)


def extract_bin_ops(file, file_id, resulting_json):
    print("Extracting calls from {}".format(file))
    tree = try_to_extract(file)
    if tree is None:
        return
    function_to_parameters = {}
    for node in ast.walk(tree):
        if not hasattr(node, 'parent'):
            node.parent = None
        for child in ast.iter_child_nodes(node):
            child.parent = node
    BinOpsCollector(function_to_parameters, file_id, file, resulting_json).visit(tree)
