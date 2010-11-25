from zope.interface.common.mapping import IFullMapping

try:
    from zope.location import LocationIterator
except ImportError:
    from zope.app.location import LocationIterator # BBB


class AbstractNode(object):
    """The base for all kinds of nodes, agnostic to the type of node

    methods defined here are only methods that use the node itself, but make no
    assumptions about where the node's data is stored. Storage specific methods
    raise NotImplementedError, that are:
    - __delitem__
    - __getitem__
    - __setitem__
    - __iter__
    If __getitem__ is expensive, also:
    - __contains__
    """
    def __init__(self, name=None, parent=None):
        self.__name__ = name
        self.__parent__ = parent

    @property
    def path(self):
        return reversed([parent.__name__ for parent in LocationIterator(self)])

    @property
    def root(self):
        root = None
        for parent in LocationIterator(self):
            root = parent
        return root

    def __contains__(self, key):
        """uses __getitem__

        This should be overriden by nodes, where __getitem__ is expensive.
        """
        try:
            self[key]
        except KeyError:
            return False
        return True
    
    def __delitem__(self, key):
        raise NotImplementedError

    def __getitem__(self, key):
        raise NotImplementedError

    def __setitem__(self, key):
        raise NotImplementedError

    def __len__(self):
        """based on keys()
        """
        return len(self.keys())

    def __iter__(self):
        raise NotImplementedError

    def get(self, key, default=None):
        """based on __getitem__
        """
        try:
            return self[key]
        except KeyError:
            return default

    def iterkeys(self):
        """returns __iter__()
        """
        return self.__iter__()

    def iteritems(self):
        """based on __iter__ and __getitem__
        """
        for key in self:
            yield key, self[key]

    def itervalues(self):
        """based on __iter and __getitem__
        """
        for key in self:
            yield self[key]

    def items(self):
        """based on iteritems
        """
        return [x for x in self.iteritems()]

    def keys(self):
        """based on __iter__
        """
        return [x for x in self]

    def values(self):
        """based on itervalues
        """
        return [x for x in self.itervalues()]


# XXX: WIP
class FilteredNodespace(object):
    def filterediter(self, flter=None):
        """Apply filter

        flter can be:
        - interface that children need to provide
        - dict 
        - ...

        XXX: use backend support if available, i.e. query keys from backend and
        return only those

        XXX: feels like a backend issue
        """
