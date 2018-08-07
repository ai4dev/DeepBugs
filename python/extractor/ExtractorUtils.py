'''
Created on 31.07.18

@author: Egor Bogomolov
'''

from io import BytesIO
from tokenize import tokenize, NUMBER, NAME, OP, STRING, AWAIT, ASYNC
from ast import Num, Str, Bytes, Name, Starred, NameConstant, Attribute, Subscript, FormattedValue, Expr, UnaryOp, \
    BinOp, BoolOp, Compare, Call, Lambda

standard_string = 'STD:{}'
literal_string = 'LIT:{}'
identifier_string = 'ID:{}'


def get_tokens(file, resulting_json):
    result = []
    with open(file) as fin:
        print("Collecting from {}".format(file))
        try:
            tokens = tokenize(BytesIO(fin.read().encode('utf-8')).readline)
        except UnicodeDecodeError:
            try:
                tokens = tokenize(BytesIO(fin.read().encode('cp1252')).readline)
            except UnicodeDecodeError:
                return

        for toknum, tokval, _, _, _ in tokens:
            if toknum in [OP, AWAIT, ASYNC]:
                result.append(standard_string.format(tokval))
            elif toknum == NUMBER:
                result.append(literal_string.format(tokval))
            elif toknum == STRING:
                result.append(literal_string.format(tokval[1:-1]))
            elif toknum == NAME:
                result.append(identifier_string.format(tokval))

    resulting_json.append(result)


def get_name_of_ast_node(node):
    if type(node) is Num:
        return literal_string.format(node.n)
    if type(node) is Str or type(node) is Bytes:
        return literal_string.format(node.s)
    if type(node) is Name:
        return identifier_string.format(node.id)
    if type(node) is NameConstant:
        return literal_string.format(node.value)
    if type(node) is Attribute:
        return identifier_string.format(node.attr)
    if type(node) is Subscript or \
            type(node) is FormattedValue or \
            type(node) is Starred or \
            type(node) is Expr:
        return get_name_of_ast_node(node.value)
    if type(node) is UnaryOp:
        return get_name_of_ast_node(node.operand)
    if type(node) is BinOp or \
            type(node is Compare):
        return get_name_of_ast_node(node.left)
    if type(node) is BoolOp:
        return get_name_of_ast_node(node.values[0])
    if type(node) is Call:
        return get_name_of_ast_node(node.func)
    if type(node) is Lambda:
        return identifier_string.format("lambda")
    return 'unknown'
