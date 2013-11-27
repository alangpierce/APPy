from collections import namedtuple

__author__ = 'alangpierce'

class Expression:
    pass

class BinaryOperator(Expression):
    def __init__(self, operator, left, right):
        self.operator = operator
        self.left = left
        self.right = right

class Literal(Expression):
    def __init__(self, value):
        self.value = value
