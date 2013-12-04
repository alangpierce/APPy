from appy_ast import Value


class TypeContext(object):

    def __init__(self):
        self.type_type = create_type_type_value()
        # TODO: Add attributes for all operations.
        # TODO: Keeping the type name in the data is kind of a hack
        # while the code transitions to making types more first-class.
        self.int_type = Value(self.type_type, 'int', {})
        self.str_type = Value(self.type_type, 'str', {})
        self.bool_type = Value(self.type_type, 'bool', {})


def create_type_type_value():
    class TypeTypeValue(Value):
        '''This is a hack so that we can make a namedtuple that
        contains itself. This should be the one case in the Python
        language where an object's type is itself, and in all other
        cases the attributes on a value are immutable.
        '''
        def __getattribute__(self, name):
            if name == 'type':
                return self
            else:
                return Value.__getattribute__(self, name)
    return TypeTypeValue(None, 'type', {})
