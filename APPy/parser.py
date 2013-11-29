from ply import yacc
from appy_ast import BinaryOperator, Literal, Value
import lexer

tokens = lexer.tokens

precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDEDBY'),
)


def p_expression_plus(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDEDBY expression
    '''
    p[0] = BinaryOperator(p[2], p[1], p[3])


def p_expression_parens(p):
    'expression : LPAREN expression RPAREN'
    p[0] = p[2]


def p_int_literal(p):
    'expression : NUMBER'
    p[0] = Literal(Value('int', p[1]))


def p_string_literal(p):
    'expression : STRING'
    p[0] = Literal(Value('str', p[1]))


def p_error(p):
    raise SyntaxError("Syntax error: " + str(p))


def create_parser():
    return yacc.yacc()

