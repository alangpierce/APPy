from appy_ast import Value


def evaluate_expression(expression):
    try:
        method = globals()['evaluate_' + expression.__class__.__name__]
    except KeyError as e:
        raise NotImplementedError(
            'Missing handler for expression ' + str(expression))
    return method(expression)


BINARY_OPERATORS = {
    '+': lambda a, b: a + b,
    '-': lambda a, b: a - b,
    '*': lambda a, b: a * b,
    '/': lambda a, b: a / b,
}


def evaluate_BinaryOperator(binop):
    func = BINARY_OPERATORS[binop.operator]
    left_value = evaluate_expression(binop.left).value
    right_value = evaluate_expression(binop.right).value
    return Value(func(left_value, right_value))


def evaluate_Literal(literal):
    return Value(literal.value)
