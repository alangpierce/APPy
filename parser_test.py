import unittest

from appy_ast import (BinaryOperator, Literal, Value, ExpressionStatement,
                      PrintStatement, IfStatement, Assignment, Variable,
                      WhileStatement, DefStatement, FunctionCall, Seq,
                      ClassStatement, PassStatement, AttributeAccess,
                      ListLiteral, GetItem)
from builtin_types import TypeContext
from lexer import create_lexer
from parser import Parser


class ParserTest(unittest.TestCase):
    def setUp(self):
        self.type_context = TypeContext()

    def test_basic_parsing(self):
        self.assert_ast_expression(
            '5 + 3',
            BinaryOperator('+', self.int_literal(5), self.int_literal(3)))

    def test_operator_precedence(self):
        self.assert_ast_expression(
            '1*2 + 5*6 - 4/2',
            BinaryOperator(
                '-',
                BinaryOperator(
                    '+',
                    BinaryOperator(
                        '*', self.int_literal(1), self.int_literal(2)),
                    BinaryOperator(
                        '*', self.int_literal(5), self.int_literal(6))),
                BinaryOperator('/', self.int_literal(4), self.int_literal(2))))

    def test_parens(self):
        self.assert_ast_expression(
            '3 * (1 + 2)',
            BinaryOperator(
                '*',
                self.int_literal(3),
                BinaryOperator('+', self.int_literal(1), self.int_literal(2))))

    def test_string_concat(self):
        self.assert_ast_expression(
            "'Hello, ' + \"world!\"",
            BinaryOperator(
                '+',
                self.string_literal('Hello, '),
                self.string_literal('world!')))

    def test_boolean_expression(self):
        self.assert_ast_expression(
            'True or False and True',
            BinaryOperator(
                'or',
                self.bool_literal(True),
                BinaryOperator(
                    'and',
                    self.bool_literal(False),
                    self.bool_literal(True))))

    def test_comparisons(self):
        self.assert_ast_expression(
            '1 == 2',
            BinaryOperator('==', self.int_literal(1), self.int_literal(2)))
        self.assert_ast_expression(
            '1 < 2',
            BinaryOperator('<', self.int_literal(1), self.int_literal(2)))
        self.assert_ast_expression(
            '1 > 2',
            BinaryOperator('>', self.int_literal(1), self.int_literal(2)))
        self.assert_ast_expression(
            '1 <= 2',
            BinaryOperator('<=', self.int_literal(1), self.int_literal(2)))
        self.assert_ast_expression(
            '1 >= 2',
            BinaryOperator('>=', self.int_literal(1), self.int_literal(2)))

    def test_print(self):
        self.assert_ast(
            'print "Hello"',
            PrintStatement(self.string_literal('Hello')))

    def test_if(self):
        self.assert_ast(
            '''
if True:
    x = 5''',
            IfStatement(self.bool_literal(True),
                        Assignment(Variable('x'), self.int_literal(5)))
        )

    def test_while(self):
        self.assert_ast(
            '''
while False:
    print "Banana"''',
            WhileStatement(
                self.bool_literal(False),
                PrintStatement(self.string_literal('Banana'))))

    def test_simple_function(self):
        self.assert_ast(
            '''
def test():
    0''',
            DefStatement('test', [], ExpressionStatement(self.int_literal(0))))

    def test_function_definition(self):
        self.assert_ast(
            '''
def foo(x):
    print x''',
            DefStatement('foo', ['x'], PrintStatement(Variable('x'))))

    def test_pass(self):
        self.assert_ast(
            '''
pass
def foo():
    pass
    print 5''',
            Seq(PassStatement(),
                DefStatement('foo', [],
                             Seq(PassStatement(),
                                 PrintStatement(self.int_literal(5))))))

    def test_function_call(self):
        self.assert_ast(
            'foo(bar, 7, x + 5)',
            ExpressionStatement(FunctionCall(
                Variable('foo'),
                [Variable('bar'), self.int_literal(7),
                 BinaryOperator('+', Variable('x'), self.int_literal(5))]))
        )

    def test_class_definition(self):
        self.assert_ast(
            '''
class Blah(object):
    x = 5
foo = Blah()''',
            Seq(ClassStatement('Blah', Variable('object'),
                               Assignment(Variable('x'), self.int_literal(5))),
                Assignment(Variable('foo'), FunctionCall(Variable('Blah'), []))
                )
        )

    def test_attribute_access(self):
        self.assert_ast(
            '''
print a.b()
print 'hello' + 'world'.capitalize()
print ('foo' + 'bar').capitalize()''',
            Seq(
                PrintStatement(
                    FunctionCall(AttributeAccess(Variable('a'), 'b'), [])),
                Seq(
                    PrintStatement(BinaryOperator(
                        '+',
                        self.string_literal('hello'),
                        FunctionCall(AttributeAccess(
                            self.string_literal('world'), 'capitalize'), []))),
                    PrintStatement(FunctionCall(AttributeAccess(
                        BinaryOperator(
                            '+', self.string_literal('foo'),
                            self.string_literal('bar')), 'capitalize'),
                        [])))))

    def test_list_literal(self):
        self.assert_ast(
            'my_list = [1, 2, foo(x)]',
            Assignment(Variable('my_list'), ListLiteral(
                [self.int_literal(1),
                 self.int_literal(2),
                 FunctionCall(Variable('foo'), [Variable('x')])])))

    def test_list_access(self):
        self.assert_ast(
            'my_list[foo() + 3]',
            ExpressionStatement(
                GetItem(Variable('my_list'),
                        BinaryOperator('+',
                                       FunctionCall(Variable('foo'), []),
                                       self.int_literal(3)))))

    def assert_ast(self, program, expected_ast):
        actual_ast = self.get_ast(program)
        self.assertEqual(expected_ast, actual_ast,
                         "\nExpected:\n" + expected_ast.pretty_print() +
                         "\n\nActual:\n" + actual_ast.pretty_print(), )

    def assert_ast_expression(self, program, expected_ast_expression):
        self.assert_ast(program, ExpressionStatement(expected_ast_expression))

    def get_ast(self, program):
        parser = Parser(self.type_context)
        lexer = create_lexer()
        return parser.parse(program, lexer)

    def int_literal(self, int_value):
        return Literal(Value(self.type_context.int_type, int_value, {}))

    def string_literal(self, string_value):
        return Literal(Value(self.type_context.str_type, string_value, {}))

    def bool_literal(self, bool_value):
        return Literal(Value(self.type_context.bool_type, bool_value, {}))


if __name__ == '__main__':
    unittest.main()
