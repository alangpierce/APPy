from appy_ast import Value, ExpressionStatement, PrintStatement, Seq, Assignment, Variable, IfStatement


def execute_statement(statement, stdout_handler, scope):
    try:
        method = globals()['execute_' + statement.__class__.__name__]
    except KeyError as e:
        raise NotImplementedError(
            'Missing handler for statement ' + str(statement))
    return method(statement, stdout_handler, scope)

def evaluate_expression(expression, scope):
    try:
        method = globals()['evaluate_' + expression.__class__.__name__]
    except KeyError as e:
        raise NotImplementedError(
            'Missing handler for expression ' + str(expression))
    return method(expression, scope)


# An "assignable", a.k.a. an lvalue, is an expression that is valid on
# the left side of an assignment. Assignables are still of type
# expression, but only some expressions are valid assignables.
def resolve_assignable(expression):
    try:
        method = globals()['resolve_' + expression.__class__.__name__]
    except KeyError as e:
        raise NotImplementedError(
            'Missing handler for assignable ' + str(expression))
    return method(expression)


def execute_Seq(statement, stdout_handler, scope):
    assert isinstance(statement, Seq)
    execute_statement(statement.left, stdout_handler, scope)
    execute_statement(statement.right, stdout_handler, scope)


def execute_Assignment(statement, stdout_handler, scope):
    assert isinstance(statement, Assignment)
    value = evaluate_expression(statement.right, scope)
    assignable = resolve_assignable(statement.left)
    if isinstance(assignable, Variable):
        scope[assignable.name] = value
    else:
        raise NotImplementedError('Unexpected assignable type: ' +
                                  assignable.__class__.__name__)


def execute_ExpressionStatement(statement, stdout_handler, scope):
    assert isinstance(statement, ExpressionStatement)
    evaluate_expression(statement.expr, scope)


def execute_PrintStatement(statement, stdout_handler, scope):
    assert isinstance(statement, PrintStatement)
    value = evaluate_expression(statement.expr, scope)
    stdout_handler(str(value.value))


def execute_IfStatement(statement, stdout_handler, scope):
    assert isinstance(statement, IfStatement)
    condition_value = evaluate_expression(statement.condition, scope)
    # TODO: This is lame and hides the interesting stuff.
    if condition_value.value:
        execute_statement(statement.statement, stdout_handler, scope)


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


def evaluate_BinaryOperator(expression, scope):
    function_by_types = BINARY_OPERATORS[expression.operator]
    left_value = evaluate_expression(expression.left, scope)
    right_value = evaluate_expression(expression.right, scope)
    try:
        func = function_by_types[(left_value.type, right_value.type)]
    except KeyError:
        raise TypeError(
            'unsupported operand type(s) for ' + expression.operator + ": '" +
            left_value.type + "' and '" + right_value.type + "'")
    (result_type, result_value) = func(left_value.value, right_value.value)
    return Value(result_type, result_value)


def evaluate_Literal(expression, scope):
    return expression.value


def evaluate_Variable(expression, scope):
    assert isinstance(expression, Variable)
    try:
        return scope[expression.name]
    except KeyError:
        raise NameError('name ' + expression.name + ' is not defined')


def resolve_Variable(expression):
    return expression
