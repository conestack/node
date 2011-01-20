from node.utils import (
    AttributeAccess,
    LocationIterator,
)


class _NodeMixin(object):
    """The base for all kinds of nodes, agnostic to the type of node.
    
    Implements contracts of ``zope.location.interfaces.ILocation`` and the one
    directly defined in ``node.intefaces.INode``.
    """
    
    def __init__(self, name=None, parent=None):
        self.__name__ = name
        self.__parent__ = parent
        # XXX: do we really need to throw error if a child is not a node
        # should we not just treat values as values and nodes as nodes and
        # don't care?
        # a: the design decision for this was due to first implementation
        # of node index, so this could probably be removed in future, lets keep
        # until node extension has been adopted to new node infrastructure.
        self.allow_non_node_childs = False
    
    @property
    def path(self):
        path = [parent.__name__ for parent in LocationIterator(self)]
        path.reverse()
        return path

    @property
    def root(self):
        root = None
        for parent in LocationIterator(self):
            root = parent
        return root
    
    def detach(self, key):
        node = self[key]
        del self[key]
        return node
    
    def filtereditervalues(self, interface):
        """Uses ``itervalues``.
        """
        for val in self.itervalues():
            if interface.providedBy(val):
                yield val
    
    def filteredvalues(self, interface):
        """Uses ``values``.
        """
        return [val for val in self.values() if interface.providedBy(val)]
    
    # BBB 2010-12-23
    filtereditems = filtereditervalues
    
    # XXX: should be implemented by a wrapper like AliasedNodespace -cfl
    def as_attribute_access(self):
        return AttributeAccess(self)
    
    @property
    def noderepr(self):
        """``noderepr`` is used in ``printtree``.
        
        Thus, we can overwrite it in subclass and return any debug information
        we need while ``__repr__`` is an enhanced standard object
        representation, also used as ``__str__`` on nodes.

        XXX: do we really need the difference or can we just override __repr__
        in subclasses and use __repr__ in printtree?
        """
        if hasattr(self.__class__, '_wrapped'):
            class_ = self.__class__._wrapped
        else:
            class_ = self.__class__
        name = unicode(self.__name__).encode('ascii', 'replace')
        return str(class_) + ': ' + name[name.find(':') + 1:]
    
    def printtree(self, indent=0):
        """Uses ``values``.
        """
        print "%s%s" % (indent * ' ', self.noderepr)
        for node in self.values():
            try:
                node.printtree(indent+2)
            except AttributeError:
                # Non-Node values are just printed
                print "%s%s" % (indent * ' ', node)

    def __repr__(self):
        if hasattr(self.__class__, '_wrapped'):
            class_name = self.__class__._wrapped.__name__
        else:
            class_name = self.__class__.__name__
        # XXX: This is mainly used in doctest, I think
        #      doctest fails if we output utf-8
        name = unicode(self.__name__).encode('ascii', 'replace')
        return "<%s object '%s' at %s>" % (class_name,
                                           name,
                                           hex(id(self))[:-1])

    __str__ = __repr__
    
    ###
    # Agnostic IFullMapping related.
    
    def copy(self):
        new = self.__class__()
        # XXX: that looks bad, would actually mean that the parent should now
        # the copy under the same name as us. What do you think about not
        # setting __name__ and __parent__, it should be a parents job to do so.
        new.__name__ = self.__name__
        new.__parent__ = self.__parent__
        new.update(self.items())
        return new


class _FullMappingMixin(object):
    """The base for all kinds of nodes not relying on an ``IFullMapping`` base
    implementation, like ``dict`` or ``odict.odict``. This excludes all nodes
    inheriting from ``BaseNode`` and ``OderedNode``.
    
    Implemented functions are agnostic to the type of node.

    Methods defined here are only methods that use the node itself, but make no
    assumptions about where the node's data is stored. Storage specific methods
    raise ``NotImplementedError``, that are:
    - ``__getitem__``
    - ``__delitem__``
    - ``__setitem__``
    - ``__iter__``
    - ``copy`` (FYI - _NodeMixin implements an agnostic ``copy`` function)
    - ``clear``
    - ``update``
    - ``setdefault``
    - ``pop``
    - ``popitem``
    """
    
    ###
    # ``IItemMapping``
    
    def __getitem__(self, key):
        raise NotImplementedError
    
    ###
    # ``IReadMapping``
    
    def get(self, key, default=None):
        """Uses ``__getitem__``.
        """
        try:
            return self[key]
        except KeyError:
            return default
    
    def __contains__(self, key):
        """Uses ``__getitem__``.

        This should be overriden by nodes, where ``__getitem__`` is expensive.

        XXX: also catching the exception is expensive, so this should be
        overriden probably always.
        """
        try:
            self[key]
        except KeyError:
            return False
        return True
    
    ###
    # ``IWriteMapping``
    
    def __delitem__(self, key):
        raise NotImplementedError
    
    def __setitem__(self, key, value):
        raise NotImplementedError
    
    ###
    # ``IEnumerableMapping``
    
    def keys(self):
        """Uses ``__iter__``.
        """
        return [x for x in self]
    
    def __iter__(self):
        raise NotImplementedError
    
    def values(self):
        """Uses ``itervalues``.
        """
        return [x for x in self.itervalues()]
    
    def items(self):
        """Uses ``iteritems``.
        """
        return [x for x in self.iteritems()]

    def __len__(self):
        """Uses ``keys``.

        XXX: there could also be faster approaches depending on implementation
        """
        return len(self.keys())
    
    ###
    # ``IIterableMapping``
    
    def iterkeys(self):
        """Uses ``__iter__``.
        """
        return self.__iter__()
    
    def itervalues(self):
        """Uses ``__iter__`` and ``__getitem__``.
        """
        for key in self:
            yield self[key]
    
    def iteritems(self):
        """Uses ``__iter__`` and ``__getitem__``.
        """
        for key in self:
            yield key, self[key]
    
    ###
    # ``IClonableMapping``
    
    def copy(self):
        raise NotImplementedError

    ###
    # ``IExtendedReadMapping``
    
    def has_key(self, key):
        return key in self

    ###
    # ``IExtendedWriteMapping``
    
    def clear(self):
        raise NotImplementedError
    
    def update(self, data=(), **kw):
        raise NotImplementedError
    
    def setdefault(self, key, default=None):
        raise NotImplementedError
    
    def pop(self, key, default=None):
        raise NotImplementedError
    
    def popitem(self):
        raise NotImplementedError


class _ImplMixin(object):
    """Abstract mixin class for different node implementations.
    
    A class utilizing this contract must inherit from choosen ``IFullMaping``.
    
    We cannot use same contract as in ``odict.odict`` -> ``_dict_impl``.
    Odict requires the dict implementation to store it's internal double linked
    list while we need to have an implementation which must provide a ready to
    use ``IFullMapping``
    """
    
    def _mapping_impl(self):
        """Return ``IFullMaping`` implementing class.
        """
        raise NotImplementedError
