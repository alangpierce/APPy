from appy_ast import (Value, ExpressionStatement, PrintStatement, Seq,
                      Assignment, Variable, IfStatement, WhileStatement)


class ExecutionEnvironment(object):
    """Tracks all state that needs to be tracked during regular
    execution, and contains the implementation of the handlers for the
    various types of expressions and statements.
    """

    def __init__(self, stdout_handler):
        self.stdout_handler = stdout_handler
        self.scope = {}

    def execute_statement(self, statement):
        try:
            method = getattr(self, 'execute_' + statement.__class__.__name__)
        except AttributeError:
            raise NotImplementedError(
                'Missing handler for statement ' + str(statement))
        return method(statement)

    def evaluate_expression(self, expression):
        try:
            method = getattr(self, 'evaluate_' + expression.__class__.__name__)
        except AttributeError:
            raise NotImplementedError(
                'Missing handler for expression ' + str(expression))
        return method(expression)


    # An "assignable", a.k.a. an lvalue, is an expression that is valid on
    # the left side of an assignment. Assignables are still of type
    # expression, but only some expressions are valid assignables.
    def resolve_assignable(self, expression):
        try:
            method = getattr(self, 'resolve_' + expression.__class__.__name__)
        except AttributeError:
            raise NotImplementedError(
                'Missing handler for assignable ' + str(expression))
        return method(expression)


    def execute_Seq(self, statement):
        assert isinstance(statement, Seq)
        self.execute_statement(statement.left)
        self.execute_statement(statement.right)


    def execute_Assignment(self, statement):
        assert isinstance(statement, Assignment)
        value = self.evaluate_expression(statement.right)
        assignable = self.resolve_assignable(statement.left)
        if isinstance(assignable, Variable):
            self.scope[assignable.name] = value
        else:
            raise NotImplementedError('Unexpected assignable type: ' +
                                      assignable.__class__.__name__)

    def execute_ExpressionStatement(self, statement):
        assert isinstance(statement, ExpressionStatement)
        self.evaluate_expression(statement.expr)

    def execute_PrintStatement(self, statement):
        assert isinstance(statement, PrintStatement)
        value = self.evaluate_expression(statement.expr)
        self.stdout_handler(str(value.value))

    def execute_IfStatement(self, statement):
        assert isinstance(statement, IfStatement)
        condition_value = self.evaluate_expression(statement.condition)
        # TODO: This is lame and hides the interesting stuff.
        if condition_value.value:
            self.execute_statement(statement.statement)

    def execute_WhileStatement(self, statement):
        assert isinstance(statement, WhileStatement)
        while True:
            condition_value = self.evaluate_expression(statement.condition)
            if not condition_value.value:
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

    def evaluate_BinaryOperator(self, expression):
        function_by_types = ExecutionEnvironment.BINARY_OPERATORS[
            expression.operator]
        left_value = self.evaluate_expression(expression.left)
        right_value = self.evaluate_expression(expression.right)
        try:
            func = function_by_types[(left_value.type, right_value.type)]
        except KeyError:
            raise TypeError(
                'unsupported operand type(s) for ' + expression.operator + ": '" +
                left_value.type + "' and '" + right_value.type + "'")
        (result_type, result_value) = func(left_value.value, right_value.value)
        return Value(result_type, result_value)

    def evaluate_Literal(self, expression):
        return expression.value

    def evaluate_Variable(self, expression):
        assert isinstance(expression, Variable)
        try:
            return self.scope[expression.name]
        except KeyError:
            raise NameError('name ' + expression.name + ' is not defined')

    def resolve_Variable(self, expression):
        return expression
