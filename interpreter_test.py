import unittest
from appy_ast import Value

from interpreter import ExecutionEnvironment, Interpreter

class InterpreterTest(unittest.TestCase):
    def setUp(self):
        self.stdout_builder = []
        stdout_handler = lambda s: self.stdout_builder.append(s)
        self.interpreter = Interpreter(stdout_handler)
        self.type_context = self.interpreter.type_context

    def test_basic_interpreter(self):
        self.assert_evaluate('5 + 3', self.int_value(8))

    def test_order_of_operations(self):
        self.assert_evaluate('1 + 2 * 3', self.int_value(7))

    def test_parens(self):
        self.assert_evaluate('5 / (1 + 1)', self.int_value(2))

    def test_string_concat(self):
        self.assert_evaluate('"hello" + "world"',
                             self.string_value('helloworld'))

    def test_string_subtract_is_illegal(self):
        self.assert_error(TypeError, '"hello" - "world"')

    def test_string_multiply_right(self):
        self.assert_evaluate('"hello" * 3',
                             self.string_value('hellohellohello'))

    def test_string_multiply_left(self):
        self.assert_evaluate('2 * "hello"', self.string_value('hellohello'))

    def test_boolean_operators(self):
        self.assert_evaluate('True or False and True', self.bool_value(True))

    def test_comparisons(self):
        self.assert_evaluate('5 == 5 and 3 < 5 and 1 != 2',
                             self.bool_value(True))
        self.assert_evaluate('1 > 3 or 100 <= 10', self.bool_value(False))

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

    def test_function_call(self):
        self.assert_execute(
            '''
def foo(x):
    print x
foo(3)''',
            '3')

    def assert_evaluate(self, program, expected_value):
        # TODO: I'm pretty sure this is doing deep equality on the
        # type, which it probably shouldn't do.
        self.assertEqual(expected_value, self.evaluate_expression(program))

    def assert_execute(self, program, expected_stdout):
        actual_stdout = self.execute_program(program)
        self.assertEqual(expected_stdout, actual_stdout)

    def assert_error(self, exception_type, program):
        self.assertRaises(exception_type, self.execute_program, program)

    def evaluate_expression(self, expression):
        return self.interpreter.evaluate_expression(expression)

    def capture_stdout(self, func):
        self.stdout_builder[:] = []
        func()
        return ''.join(self.stdout_builder)

    # Returns the output from stdout
    def execute_program(self, program):
        return self.capture_stdout(
            lambda: self.interpreter.execute_program(program))

    def int_value(self, int_val):
        return Value(self.type_context.int_type, int_val, {})

    def string_value(self, string_val):
        return Value(self.type_context.str_type, string_val, {})

    def bool_value(self, bool_val):
        return Value(self.type_context.bool_type, bool_val, {})


if __name__ == '__main__':
    unittest.main()
