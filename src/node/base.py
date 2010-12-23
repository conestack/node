import inspect
from odict import odict
from zope.interface import implements
from interfaces import INode
from utils import (
    AttributeAccess,
    LocationIterator)


###############################################################################
# Base mixin classes
###############################################################################

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
    
    # XXX: inconsistent naming, filteredvalues() as values() should return a
    # list, not an iterator
    def filteredvalues(self, interface):
        """Uses ``values``.
        """
        for node in self.values():
            if interface.providedBy(node):
                yield node
    
    # BBB
    filtereditems = filteredvalues
    
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


class _NodeSpaceMixin(_NodeMixin, _ImplMixin):
    """Base nodespace support.
    
    Still an abstract implementation.
    
    Subclass must inherit from this object and an ``IFullMapping`` implementing
    object and return its class in ``self._mapping_impl()``.
    """
    
    def __init__(self, name=None, parent=None):
        """
        ``name``
            Optional name used for ``__name__`` declared by ``ILocation``.
        """
        self._mapping_impl().__init__(self)
        _NodeMixin.__init__(self, name, parent)
        self._nodespaces = None
    
    @property
    def nodespaces(self):
        """A storage and general way to access our nodespaces.
        
        An ``AttributedNode`` uses this to store the ``attrs`` nodespace i.e.
        """
        if self._nodespaces is None:
            self._nodespaces = odict()
            self._nodespaces['__children__'] = self
        return self._nodespaces
    
    def __getitem__(self, key):
        # blend in our nodespaces as children, with name __<name>__
        # isinstance check is required because odict tries to get item possibly
        # with ``_nil`` key, which is actually an object
        if isinstance(key, basestring) \
          and key.startswith('__') \
          and key.endswith('__'):
            # a reserved child key mapped to the nodespace behind
            # nodespaces[key], nodespaces is an odict
            return self.nodespaces[key]
        try:
            return self._mapping_impl().__getitem__(self, key)
        except KeyError:
            # XXX: do we really want to relocate this exception?
            raise KeyError(key)
    
    def __setitem__(self, key, val):
        # XXX: checking against ``_NodeMixin`` instance requires all node
        #      implementations to inherit from it. Check wether
        #      ``INode.providedBy`` is slower than ``isinstance``.
        #is_node = isinstance(val, _NodeMixin)
        is_node = INode.providedBy(val)
        if is_node:
            # XXX: do we really want to adopt nodespaces or move below next if
            # I think so far we did, but not sure
            val.__name__ = key
            val.__parent__ = self
        # blend in our nodespaces as children, with name __<name>__
        if key.startswith('__') and key.endswith('__'):
            # a reserved child key mapped to the nodespace behind
            # nodespaces[key], nodespaces is an odict
            self.nodespaces[key] = val
            # index checks below must not happen for other nodespace.
            return
        if not self.allow_non_node_childs and inspect.isclass(val):
            raise ValueError, u"It isn't allowed to use classes as values."
        if not self.allow_non_node_childs and not is_node:
            raise ValueError("Non-node childs are not allowed.")
        self._mapping_impl().__setitem__(self, key, val)
    
    def __delitem__(self, key):
        # blend in our nodespaces as children, with name __<name>__
        if key.startswith('__') and key.endswith('__'):
            # a reserved child key mapped to the nodespace behind
            # nodespaces[key], nodespaces is an odict
            del self.nodespaces[key]
            return
        # fail immediately if key does not exist
        # XXX: do we need this check for lazynodes?
        # XXX: it feels like calling next __delitem__ could be enough
        self[key]
        self._mapping_impl().__delitem__(self, key)


###############################################################################
# base nodes
###############################################################################

class AbstractNode(_NodeMixin, _FullMappingMixin):
    """An abstract Node.
    
    Derive this if you like to implement all storage related functions on your
    own.
    """
    implements(INode)


class BaseNode(_NodeSpaceMixin, dict):
    """Base node, not ordered.
    
    Uses ``dict`` as ``IFullMapping`` implementation.
    
    Derive this for unordered trees.
    """
    implements(INode)
    
    def _mapping_impl(self):
        return dict
    
    def update(self, data=(), **kw):
        for key, value in data:
            self[key] = value
        for key, value in kw.items():
            self[key] = value
    
    def setdefault(self, key, value=None):
        try:
            return self[key]
        except KeyError:
            self[key] = value
            return value


class OrderedNode(_NodeSpaceMixin, odict):
    """Ordered node.
    
    Uses ``odict`` as ``IFullMapping`` implementation.
    
    Derive this for ordered trees.
    """
    implements(INode)
    
    def _mapping_impl(self):
        return odict
