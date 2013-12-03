import unittest

from appy_ast import Value, ExpressionStatement
from interpreter import ExecutionEnvironment
from lexer import create_lexer
from parser import create_parser


def int_value(int_val):
    return Value('int', int_val, {})


def string_value(string_val):
    return Value('str', string_val, {})


def bool_value(bool_val):
    return Value('bool', bool_val, {})


class InterpreterTest(unittest.TestCase):
    def test_basic_interpreter(self):
        self.assert_evaluate('5 + 3', int_value(8))

    def test_order_of_operations(self):
        self.assert_evaluate('1 + 2 * 3', int_value(7))

    def test_parens(self):
        self.assert_evaluate('5 / (1 + 1)', int_value(2))

    def test_string_concat(self):
        self.assert_evaluate('"hello" + "world"', string_value('helloworld'))

    def test_string_subtract_is_illegal(self):
        self.assert_error(TypeError, '"hello" - "world"')

    def test_string_multiply_right(self):
        self.assert_evaluate('"hello" * 3', string_value('hellohellohello'))

    def test_string_multiply_left(self):
        self.assert_evaluate('2 * "hello"', string_value('hellohello'))

    def test_boolean_operators(self):
        self.assert_evaluate('True or False and True', bool_value(True))

    def test_comparisons(self):
        self.assert_evaluate('5 == 5 and 3 < 5 and 1 != 2', bool_value(True))
        self.assert_evaluate('1 > 3 or 100 <= 10', bool_value(False))

    def test_print(self):
        self.assert_execute('print "Hello"', "Hello")

    def test_assignment(self):
        self.assert_execute(
            '''
x = 5
print x + 3
''',
            '8')

    def test_illegal_variable(self):
        self.assert_error(NameError, 'foo + 5')

    def test_if(self):
        self.assert_execute(
            '''
x = 7
if x > 5:
    print 'Greater'
''',
        'Greater')

    def test_while(self):
        self.assert_execute(
            '''
sum = 0
i = 0
while i <= 10:
    sum = sum + i
    i = i + 1
print sum
''',
        '55'
        )

    def assert_evaluate(self, program, expected_value):
        ast = self.get_ast(program)
        assert isinstance(ast, ExpressionStatement)
        self.assertEqual(expected_value, self.evaluate_expression(ast.expr))

    def assert_execute(self, program, expected_stdout):
        ast = self.get_ast(program)
        actual_stdout = self.execute_statement(ast)
        self.assertEqual(expected_stdout, actual_stdout)

    def assert_error(self, exception_type, program):
        ast = self.get_ast(program)
        self.assertRaises(
            exception_type, self.execute_statement, ast)

    def get_ast(self, program):
        parser = create_parser()
        lexer = create_lexer()
        return parser.parse(program, lexer)

    def evaluate_expression(self, expression):
        environment = ExecutionEnvironment(lambda: None)
        return environment.evaluate_expression(expression)

    # Returns the output from stdout
    def execute_statement(self, statement):
        stdout_builder = []
        stdout_handler = lambda s: stdout_builder.append(s)
        environment = ExecutionEnvironment(stdout_handler)
        environment.execute_statement(statement)
        return ''.join(stdout_builder)


if __name__ == '__main__':
    unittest.main()
