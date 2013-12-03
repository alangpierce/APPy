from ply import yacc
from appy_ast import (BinaryOperator, Literal, Value, Assignment, Variable,
                      Seq, ExpressionStatement, PrintStatement, IfStatement, WhileStatement)
import lexer


class Parser(object):

    def __init__(self):
        self.yacc_parser = yacc.yacc(module=self)

    def parse(self, program, lexer):
        return self.yacc_parser.parse(program, lexer)

    tokens = lexer.tokens

    precedence = (
        ('left', 'OR'),
        ('left', 'AND'),
        ('left', 'EQUALS', 'NOTEQUAL', 'LESSTHAN', 'GREATERTHAN',
         'LESSTHANOREQUAL', 'GREATERTHANOREQUAL'),
        ('left', 'PLUS', 'MINUS'),
        ('left', 'TIMES', 'DIVIDEDBY'),
    )

    def p_seq(self, p):
        '''statement : statement statement'''
        p[0] = Seq(p[1], p[2])

    def p_expression_statement(self, p):
        '''statement : expression NEWLINE'''
        p[0] = ExpressionStatement(p[1])

    def p_assignment_statement(self, p):
        '''statement : expression ASSIGN expression NEWLINE'''
        p[0] = Assignment(p[1], p[3])

    def p_print_statement(self, p):
        '''statement : PRINT expression NEWLINE'''
        p[0] = PrintStatement(p[2])

    def p_if_statement(self, p):
        '''statement : IF expression COLON NEWLINE INDENT statement DEDENT'''
        p[0] = IfStatement(p[2], p[6])

    def p_while_statement(self, p):
        '''statement : WHILE expression COLON NEWLINE INDENT statement DEDENT'''
        p[0] = WhileStatement(p[2], p[6])

    def p_expression_plus(self, p):
        '''expression : expression PLUS expression
                      | expression MINUS expression
                      | expression TIMES expression
                      | expression DIVIDEDBY expression
                      | expression EQUALS expression
                      | expression NOTEQUAL expression
                      | expression LESSTHAN expression
                      | expression GREATERTHAN expression
                      | expression LESSTHANOREQUAL expression
                      | expression GREATERTHANOREQUAL expression
                      | expression AND expression
                      | expression OR expression
        '''
        p[0] = BinaryOperator(p[2], p[1], p[3])

    def p_expression_parens(self, p):
        'expression : LPAREN expression RPAREN'
        p[0] = p[2]

    def p_int_literal(self, p):
        'expression : NUMBER'
        p[0] = Literal(Value('int', p[1], {}))

    def p_bool_literal(self, p):
        '''expression : TRUE
                      | FALSE
        '''
        p[0] = Literal(Value('bool', p[1], {}))

    def p_string_literal(self, p):
        'expression : STRING'
        p[0] = Literal(Value('str', p[1], {}))

    def p_variable(self, p):
        'expression : ID'
        p[0] = Variable(p[1])

    def p_error(self, p):
        raise SyntaxError("Syntax error: " + str(p))
