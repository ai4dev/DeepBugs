'''
Created on 31.07.18
@author: Egor Bogomolov
'''

from io import BytesIO
from io import StringIO
from tokenize import tokenize, NUMBER, NAME, OP, STRING, generate_tokens, TokenError
from ast import Num, Str, Name, Attribute, Subscript, Expr, UnaryOp, \
    BinOp, BoolOp, Compare, Call, Lambda, USub, Not, Index, \
    Add, Sub, Mult, Div, FloorDiv, Mod, Pow, LShift, RShift, BitOr, BitXor, BitAnd, \
    Eq, NotEq, Lt, LtE, Gt, GtE, Is, IsNot, In, NotIn, Mod
import os.path

#import asttokens
from asttokens import ASTTokens

standard_string = 'STD:{}'
literal_string = 'LIT:{}'
identifier_string = 'ID:{}'


class NodeTypes:
    number = "number"
    string = "string"
    true = "boolean"
    false = "boolean"
    object = "object"
    none = "none"
    unknown = "unknown"
    lambdaexpr = "lambda"

def get_tokens(file, resulting_json):
    result = []

    with open(file) as fin:
        print("Collecting from {}".format(file))
        try:
            tokens = generate_tokens(BytesIO(fin.read().encode('utf-8')).readline)
        except UnicodeDecodeError:
            try:
                tokens = generate_tokens(BytesIO(fin.read().encode("cp1252")).readline)
            except UnicodeDecodeError:
                return
        if tokens is None:
            return
        last = (-1, "")
        for toknum, tokval, _, _, _ in tokens:
            if toknum == OP:
                result.append(standard_string.format(tokval))
            elif toknum == NUMBER:
                if last == (OP, "-"):
                    result.pop(-1)
                    result.append(literal_string.format("-" + tokval))
                else:
                    result.append(literal_string.format(tokval))
            elif toknum == STRING:
                result.append(literal_string.format(tokval[1:-1]))
            elif toknum == NAME:
                result.append(identifier_string.format(tokval))
            else:
                result.append(standard_string.format(tokval))
            last = (toknum, tokval)
    resulting_json.append(result)


def num_to_padded_str(num, length):
    str_num = str(num)
    while len(str_num) < length:
        str_num = '0' + str_num
    return str_num


def get_location_of_ast_node(node):
    start, end = node.first_token.startpos, node.last_token.endpos
    diff = end - start
    return num_to_padded_str(start, 6) + num_to_padded_str(diff, 4)


def get_name_of_ast_node(node):
    try:
        if type(node) is Num:
            return literal_string.format(node.n)
        if type(node) is Str:
            return literal_string.format(node.s.decode('utf-8'))
        if type(node) is Name:
            return identifier_string.format(node.id.decode('utf-8'))
        if type(node) is Attribute:
            return identifier_string.format(node.attr.decode('utf-8'))
        if type(node) is Subscript or \
                type(node) is Expr or \
                type(node) is Index:
            return get_name_of_ast_node(node.value)
        if type(node) is UnaryOp:
            if type(node.op) is USub and type(node.operand) is Num:
                return literal_string.format(-node.operand.n)
            return get_name_of_ast_node(node.operand)
        if type(node) is BinOp or \
                type(node) is Compare:
            return None
        if type(node) is BoolOp:
            return None
        if type(node) is Call:
            return get_name_of_ast_node(node.func)
        if type(node) is Lambda:
            return identifier_string.format("lambda")
        return None
    except UnicodeEncodeError:
        return None
    except UnicodeDecodeError:
        return None


def get_operation_token(op):
    if type(op) is Add:
        return '+'
    elif type(op) is Sub:
        return '-'
    elif type(op) is Mult:
        return '*'
    elif type(op) is Div:
        return '/'
    elif type(op) is FloorDiv:
        return '//'
    elif type(op) is Mod:
        return '%'
    elif type(op) is Pow:
        return '**'
    elif type(op) is LShift:
        return '<<'
    elif type(op) is RShift:
        return '>>'
    elif type(op) is BitOr:
        return '|'
    elif type(op) is BitXor:
        return '^'
    elif type(op) is BitAnd:
        return '&'
    elif type(op) is Eq:
        return '=='
    elif type(op) is NotEq:
        return '!='
    elif type(op) is Lt:
        return '<'
    elif type(op) is LtE:
        return '<='
    elif type(op) is Gt:
        return '>'
    elif type(op) is GtE:
        return '>='
    elif type(op) is Is:
        return 'is'
    elif type(op) is IsNot:
        return 'is not'
    elif type(op) is In:
        return 'in'
    elif type(op) is NotIn:
        return 'not in'
    return None



def get_base_of_ast_node(node):
    if type(node) is Attribute:
        return get_name_of_ast_node(node.value)
    elif type(node) is Subscript:
        return get_base_of_ast_node(node.value)
    return ""


def get_type_of_ast_node(node):
    if type(node) is Num:
        return NodeTypes.number
    if type(node) is Str:
        return NodeTypes.string
    if type(node) is Name:
        if node.id == 'True':
            return NodeTypes.true
        elif node.id == 'False':
            return NodeTypes.false
        elif node.id == 'None':
            return NodeTypes.none
        elif node.id == 'self':
            return NodeTypes.object
    if type(node) is Index:
        return get_type_of_ast_node(node.value)
    if type(node) is UnaryOp:
        if type(node.op) is Not:
            operand_type = get_type_of_ast_node(node.operand)
            if operand_type == NodeTypes.false:
                return NodeTypes.true
            if operand_type == NodeTypes.true:
                return NodeTypes.false
            return NodeTypes.unknown
        return get_type_of_ast_node(node.operand)
    if type(node) is Lambda:
        return NodeTypes.lambdaexpr
    return NodeTypes.unknown

def try_to_extract(file):
    if not os.path.isfile(file):
        return None
    with open(file) as fin:
        try:
            atok = ASTTokens(fin.read().encode('utf-8'), parse=True, filename=file)
        except TokenError:
            try:
                atok = ASTTokens(fin.read().encode("cp1252"), parse=True, filename=file)
            except TokenError:
                print ("Unable to extract from {}".format(file))
                return None
        except SyntaxError:
            try:
                atok = ASTTokens(fin.read().encode("cp1252"), parse=True, filename=file)
            except SyntaxError:
                print ("Unable to extract from {}".format(file))
                return None
        except ValueError:
            try:
                atok = ASTTokens(fin.read().encode("cp1252"), parse=True, filename=file)
            except ValueError:
                print ("Unable to extract from {}".format(file))
                return None
        except IndexError:
            try:
                atok = ASTTokens(fin.read().encode("cp1252"), parse=True, filename=file)
            except IndexError:
                print ("Unable to extract from {}".format(file))
                return None
        except TypeError:
            try:
                atok = ASTTokens(fin.read().encode("cp1252"), parse=True, filename=file)
            except TypeError:
                print ("Unable to extract from {}".format(file))
                return None
    return atok.tree
