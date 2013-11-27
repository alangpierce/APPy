from ply import yacc
from appy_ast import BinaryOperator, Literal
from lexer import tokens

def p_expression_add(p):
    'expression : expression PLUS expression'
    p[0] = BinaryOperator(p[2], p[1], p[3])

def p_expression_literal(p):
    'expression : NUMBER'
    p[0] = Literal(p[1])

def create_parser():
    return yacc.yacc()

