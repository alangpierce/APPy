
class ScopeChain(object):
    """
    Hierarchy of scopes. Each scope level refers to a mutable mapping
    from variable to Value, but the chain itself is immutable.

    To match Python assignment semantics, only the most local scope can
    be assigned to.
    """
    def __init__(self, parent=None, mappings=None):
        """
        @type parent: ScopeChain
        """
        if mappings is None:
            mappings = {}
        self.parent = parent
        self.mappings = mappings

    def with_pushed_mappings(self, mappings):
        return ScopeChain(self, mappings)

    def resolve_name(self, name):
        local_result = self.mappings.get(name, None)
        if local_result is not None:
            return local_result
        if self.parent is not None:
            return self.parent.resolve_name(name)
        else:
            raise NameError('name ' + name + ' is not defined')

    def assign_name(self, name, value):
        self.mappings[name] = value
