'''
Created on 31.07.18

@author: Egor Bogomolov
'''

from io import BytesIO
from tokenize import tokenize, NUMBER, NAME, OP, STRING, AWAIT, ASYNC


standard_string = 'STD:{}'
literal_string = 'LIT:{}'
identifier_string = 'ID:{}'


def get_tokens(file):
    result = []
    with open(file) as fin:
        print("Collecting from {}".format(file))
        try:
            tokens = tokenize(BytesIO(fin.read().encode('utf-8')).readline)
        except UnicodeDecodeError:
            try:
                tokens = tokenize(BytesIO(fin.read().encode('cp1252')).readline)
            except UnicodeDecodeError:
                return None

        for toknum, tokval, _, _, _ in tokens:
            if toknum in [OP, AWAIT, ASYNC]:
                result.append(standard_string.format(tokval))
            elif toknum == NUMBER:
                result.append(literal_string.format(tokval))
            elif toknum == STRING:
                result.append(literal_string.format(tokval[1:-1]))
            elif toknum == NAME:
                result.append(identifier_string.format(tokval))

    return result
