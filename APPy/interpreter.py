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
    },
    '-': {
        ('int', 'int'): lambda a, b: ('int', a - b),
    },
    '*': {
        ('int', 'int'): lambda a, b: ('int', a * b),
    },
    '/': {
        ('int', 'int'): lambda a, b: ('int', a / b),
    }
}


def evaluate_BinaryOperator(binop):
    function_by_types = BINARY_OPERATORS[binop.operator]
    left_value = evaluate_expression(binop.left)
    right_value = evaluate_expression(binop.right)
    func = function_by_types[(left_value.type, right_value.type)]
    (result_type, result_value) = func(left_value.value, right_value.value)
    return Value(result_type, result_value)


def evaluate_Literal(literal):
    return literal.value
