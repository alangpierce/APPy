from appy_ast import Value


def evaluate_expression(expression):
    return globals()['evaluate_' + expression.__class__.__name__](expression)


def evaluate_BinaryOperator(binop):
    if binop.operator == '+':
        return Value(evaluate_expression(binop.left).value + \
                     evaluate_expression(binop.right).value)
    raise SyntaxError


def evaluate_Literal(literal):
    return Value(literal.value)
