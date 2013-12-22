from appy_ast import Value


class TypeContext(object):

    def __init__(self):
        self.type_type = create_type_type_value()
        self.function_type = Value(self.type_type, "function", {})
        self.int_type = Value(self.type_type, "int", {})
        self.str_type = Value(self.type_type, "str", {})
        self.bool_type = Value(self.type_type, "bool", {})

        # We build empty types up front, then populate them, so that we
        # can refer to the types within builtin functions.
        self._define_primitive_func(
            lambda a, b: a + b, 'int', 'int', '__add__', 'int')
        self._define_primitive_func(
            lambda a, b: a and b, 'bool', 'bool', '__and__', 'bool')
        self._define_primitive_func(
            lambda a, b: a or b, 'bool', 'bool', '__or__', 'bool')

        for name, func in [('__add__', lambda a, b: a + b),
                           ('__sub__', lambda a, b: a - b),
                           ('__floordiv__', lambda a, b: a / b)]:
            self._define_primitive_func(func, 'int', 'int', name, 'int')

        self._define_primitive_func(
            lambda a, b: a + b, 'str', 'str', '__add__', 'str')
        self._define_primitive_func(
            lambda a, b: a * b, 'str', 'str', '__mul__', 'int')

        # Right now multiplication is the only special case where the
        # argument on the right could be either a string or an int.
        def dynamic_multiply(arg1, arg2):
            if arg2.type is self.int_type:
                return Value(self.int_type, arg1.data * arg2.data, {})
            elif arg2.type is self.str_type:
                return Value(self.str_type, arg1.data * arg2.data, {})
            else:
                raise "Unexpected second arg type: " + str(arg2.type)
        self.int_type.attributes['__mul__'] = \
            self._make_function(dynamic_multiply)

        for name, func in [('__eq__', lambda a, b: a == b),
                           ('__ne__', lambda a, b: a != b),
                           ('__lt__', lambda a, b: a < b),
                           ('__gt__', lambda a, b: a > b),
                           ('__le__', lambda a, b: a <= b),
                           ('__ge__', lambda a, b: a >= b)]:
            self._define_primitive_func(func, 'bool', 'int', name, 'int')

        def type_constructor(class_value):
            return Value(class_value, None, {})
        self.type_type.attributes['__call__'] = self._make_function(
            type_constructor)

    def _define_primitive_func(self, func, return_type_name, base_type_name,
                               func_name, *arg_type_names):
        base_type = self._resolve_primitive(base_type_name)
        return_type = self._resolve_primitive(return_type_name)
        arg_types = tuple(self._resolve_primitive(t) for t in arg_type_names)
        base_type.attributes[func_name] = self._make_primitive_function(
            return_type, func, *((base_type,) + arg_types))

    def _resolve_primitive(self, primitive_name):
        return getattr(self, primitive_name + '_type')

    def _make_primitive_function(self, return_type, primitive_function,
                                 *input_types):
        def result_fun(*result_args):
            actual_types = tuple(arg.type for arg in result_args)
            if actual_types != input_types:
                raise TypeError('Unexpected type: ' + str(input_types))

            result_data = primitive_function(
                *(arg.data for arg in result_args))
            return Value(return_type, result_data, {})
        return self._make_function(result_fun)

    # Note that this method should not be called in __init__ until the
    # function_type attribute has been set.
    def _make_function(self, func):
        """
        @type func: Python function (in the host runtime) that takes some
        number of Value types and returns a Value type.
        @rtype : Value
        """
        return Value(self.function_type, func, {})


def create_type_type_value():
    class TypeTypeValue(Value):
        """This is a hack so that we can make a namedtuple that
        contains itself. This should be the one case in the Python
        language where an object's type is itself, and in all other
        cases the attributes on a value are immutable.
        """
        def __getattribute__(self, name):
            if name == 'type':
                return self
            else:
                return Value.__getattribute__(self, name)
    return TypeTypeValue(None, 'type', {})
