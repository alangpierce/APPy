from appy_ast import Value


def evaluate_expression(expression):
    try:
        method = globals()['evaluate_' + expression.__class__.__name__]
    except KeyError as e:
        raise NotImplementedError(
            'Missing handler for expression ' + str(expression))
    return method(expression)


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
    }
}


def evaluate_BinaryOperator(binop):
    function_by_types = BINARY_OPERATORS[binop.operator]
    left_value = evaluate_expression(binop.left)
    right_value = evaluate_expression(binop.right)
    try:
        func = function_by_types[(left_value.type, right_value.type)]
    except KeyError:
        raise TypeError('unsupported operand type(s) for ' + binop.operator +
            ": '" + left_value.type + "' and '" + right_value.type + "'")
    (result_type, result_value) = func(left_value.value, right_value.value)
    return Value(result_type, result_value)


def evaluate_Literal(literal):
    return literal.value
