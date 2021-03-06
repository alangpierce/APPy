import unittest
from appy_ast import Value

from interpreter import ExecutionEnvironment, Interpreter

class InterpreterTest(unittest.TestCase):
    def setUp(self):
        self.stdout_builder = []
        stdout_handler = lambda s: self.stdout_builder.append(s + '\n')
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
        self.assert_execute('print "Hello"', "Hello\n")

    def test_assignment(self):
        self.assert_execute(
            '''
x = 5
print x + 3
''',
            '8\n')

    def test_illegal_variable(self):
        self.assert_error(NameError, 'foo + 5')

    def test_if(self):
        self.assert_execute(
            '''
x = 7
if x > 5:
    print 'Greater'
''',
        'Greater\n')

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
        '55\n'
        )

    def test_function_call(self):
        self.assert_execute(
            '''
def foo(x):
    print x
foo(3)''',
            '3\n')

    def test_pass(self):
        self.assert_execute(
            '''
pass
def foo1():
    pass
def foo2():
    pass
    print 5
foo1()
foo2()''',
            '5\n')

    def test_closure(self):
        self.assert_execute(
            '''
x = 5
def print_num():
    print x
print_num()''',
            '5\n')

    def test_modify_outer_scope(self):
        self.assert_execute(
            '''
x = 1
def print_num():
    print x
print_num()
x = 2
print_num()''',
            '1\n2\n'
        )

    def test_out_of_scope_access(self):
        self.assert_error(NameError, '''
def foo():
    print x

def bar():
    x = 5
    foo()

bar()''')

    def test_class_attributes(self):
        self.assert_execute(
            '''
class Foo(object):
    pass

x = Foo()
x.bar = 5
print x.bar''',
            '5\n')

    def test_class_method(self):
        self.assert_execute(
            '''
class Foo(object):
    def bar(self):
        print 'Hello'

x = Foo()
x.bar()''',
            'Hello\n')

    def test_class_data(self):
        self.assert_execute(
            '''
class SimpleClass(object):
    def reset_x(self):
        self.x = 0

instance = SimpleClass()
instance.x = 5
print instance.x
instance.reset_x()
print instance.x''',
            '5\n0\n')

    def test_list_literal(self):
        self.assert_execute(
            '''
my_list = [5, 2, 8, 3]
print my_list[1]''',
            '2\n')

    def test_list_assignment(self):
        self.assert_execute(
            '''
my_list = [5, 8, 1]
print my_list[0]
my_list[0] = 12
print my_list[0]''',
            '5\n12\n')

    def test_none(self):
        self.assert_execute(
            '''
x = None
if x is None:
    print "x was none"''',
            'x was none\n')

    def test_canonical_values(self):
        self.assert_execute(
            '''
def print_if_true(b):
    if b:
        print '!'
print_if_true((False or False) is False)
print_if_true(None is None)
print_if_true(True is (True and True))
print_if_true((True is True) is True)''',
            '!\n!\n!\n!\n')

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
