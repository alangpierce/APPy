from appy_ast import (Value, ExpressionStatement, PrintStatement, Seq,
                      Assignment, Variable, IfStatement, WhileStatement)
from builtin_types import TypeContext
from lexer import create_lexer
from parser import Parser


class Interpreter(object):
    def __init__(self, stdout_handler):
        self.stdout_handler = stdout_handler
        self.type_context = TypeContext()

    def execute_program(self, program):
        '''
        Executes a program from the top level. Use the stdout_handler
        to capture the output.
        @type program: str
        @param program: Text of program to execute.
        '''
        executor = ExecutionEnvironment(self.stdout_handler, self.type_context)
        ast = self._parse(program, self.type_context)
        executor.execute_statement(ast)

    def evaluate_expression(self, expression):
        '''
        @type expression: str
        @param expression:
        @return: A native Python value corresponding to the evaluated
        value of the expression, which must be a native Python type.
        '''
        executor = ExecutionEnvironment(self.stdout_handler, self.type_context)
        ast = self._parse(expression, self.type_context)
        assert isinstance(ast, ExpressionStatement)
        expr_ast = ast.expr
        return executor.evaluate_expression(expr_ast)

    def _parse(self, program, type_context):
        parser = Parser(type_context)
        lexer = create_lexer()
        return parser.parse(program, lexer)



class ExecutionEnvironment(object):
    """Tracks all state that needs to be tracked during regular
    execution, and contains the implementation of the handlers for the
    various types of expressions and statements.
    """

    def __init__(self, stdout_handler, type_context):
        """
        @type type_context: TypeContext
        """
        self.stdout_handler = stdout_handler
        self.scope = {}
        self.type_context = type_context

    def execute_statement(self, statement):
        try:
            method = getattr(self, '_execute_' + statement.__class__.__name__)
        except AttributeError:
            raise NotImplementedError(
                'Missing handler for statement ' + str(statement))
        return method(statement)

    def evaluate_expression(self, expression):
        try:
            method = getattr(
                self, '_evaluate_' + expression.__class__.__name__)
        except AttributeError:
            raise NotImplementedError(
                'Missing handler for expression ' + str(expression))
        return method(expression)


    # An "assignable", a.k.a. an lvalue, is an expression that is valid on
    # the left side of an assignment. Assignables are still of type
    # expression, but only some expressions are valid assignables.
    def resolve_assignable(self, expression):
        try:
            method = getattr(self, '_resolve_' + expression.__class__.__name__)
        except AttributeError:
            raise NotImplementedError(
                'Missing handler for assignable ' + str(expression))
        return method(expression)


    def _execute_Seq(self, statement):
        assert isinstance(statement, Seq)
        self.execute_statement(statement.left)
        self.execute_statement(statement.right)


    def _execute_Assignment(self, statement):
        assert isinstance(statement, Assignment)
        value = self.evaluate_expression(statement.right)
        assignable = self.resolve_assignable(statement.left)
        if isinstance(assignable, Variable):
            self.scope[assignable.name] = value
        else:
            raise NotImplementedError('Unexpected assignable type: ' +
                                      assignable.__class__.__name__)

    def _execute_ExpressionStatement(self, statement):
        assert isinstance(statement, ExpressionStatement)
        self.evaluate_expression(statement.expr)

    def _execute_PrintStatement(self, statement):
        assert isinstance(statement, PrintStatement)
        value = self.evaluate_expression(statement.expr)
        self.stdout_handler(str(value.data))

    def _execute_IfStatement(self, statement):
        assert isinstance(statement, IfStatement)
        condition_value = self.evaluate_expression(statement.condition)
        # TODO: This is lame and hides the interesting stuff.
        if condition_value.data:
            self.execute_statement(statement.statement)

    def _execute_WhileStatement(self, statement):
        assert isinstance(statement, WhileStatement)
        while True:
            condition_value = self.evaluate_expression(statement.condition)
            if not condition_value.data:
                break
            self.execute_statement(statement.statement)

    BINARY_OPERATORS = {
        '+': {
            ('int', 'int'): lambda a, b: ('int', a + b),
            ('str', 'str'): lambda a, b: ('str', a + b),
        },
        '-': {
            ('int', 'int'): lambda a, b: ('int', a - b),
        },
        '*': {
            ('int', 'int'): lambda a, b: ('int', a * b),
            ('str', 'int'): lambda a, b: ('str', a * b),
            ('int', 'str'): lambda a, b: ('str', a * b),
        },
        '/': {
            ('int', 'int'): lambda a, b: ('int', a / b),
        },
        '==': {
            ('int', 'int'): lambda a, b: ('bool', a == b)
        },
        '!=': {
            ('int', 'int'): lambda a, b: ('bool', a != b)
        },
        '<': {
            ('int', 'int'): lambda a, b: ('bool', a < b)
        },
        '>': {
            ('int', 'int'): lambda a, b: ('bool', a > b)
        },
        '<=': {
            ('int', 'int'): lambda a, b: ('bool', a <= b)
        },
        '>=': {
            ('int', 'int'): lambda a, b: ('bool', a >= b)
        },
        # TODO: Short circuit
        'and': {
            ('bool', 'bool'): lambda a, b: ('bool', a and b)
        },
        'or': {
            ('bool', 'bool'): lambda a, b: ('bool', a or b)
        }
    }

    def _evaluate_BinaryOperator(self, expression):
        function_by_types = self.BINARY_OPERATORS[expression.operator]
        left_value = self.evaluate_expression(expression.left)
        right_value = self.evaluate_expression(expression.right)
        try:
            func = function_by_types[
                (left_value.type.data, right_value.type.data)]
        except KeyError:
            raise TypeError(
                'unsupported operand type(s) for ' + expression.operator +
                ": '" + left_value.type.data + "' and '" +
                right_value.type.data + "'")
        (result_type_name, result_value) = func(
            left_value.data, right_value.data)
        return Value(
            getattr(self.type_context, result_type_name + '_type'),
            result_value,
            {})

    def _evaluate_Literal(self, expression):
        return expression.value

    def _evaluate_Variable(self, expression):
        assert isinstance(expression, Variable)
        try:
            return self.scope[expression.name]
        except KeyError:
            raise NameError('name ' + expression.name + ' is not defined')

    def _resolve_Variable(self, expression):
        return expression
