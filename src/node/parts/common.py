import uuid
import inspect
from odict import odict
from plumber import (
    Part,
    default,
    extend,
    finalize,
    plumb,
)
from zope.interface import implements
from node.interfaces import (
    INode,
    IAdopt,
    IAsAttrAccess,
    IChildFactory,
    IFixedChildren,
    IGetattrChildren,
    INodeChildValidate,
    IUnicodeAware,
    IUUIDAware,
    #IWrap,
)
from node.utils import (
    AttributeAccess,
    encode,
    decode,
)


class Adopt(Part):
    implements(IAdopt)

    @plumb
    def __setitem__(_next, self, key, val):
        # only care about adopting if we have a node
        if not INode.providedBy(val):
            _next(self, key, val)
            return

        # save old __parent__ and __name__ to restore if something goes wrong
        old_name = val.__name__
        old_parent = val.__parent__
        val.__name__ = key
        val.__parent__ = self
        try:
            _next(self, key, val)
        except (AttributeError, KeyError, ValueError):
            # XXX: In what other cases do we want to revert adoption?
            val.__name__ = old_name
            val.__parent__ = old_parent
            raise

    @plumb
    def setdefault(_next, self, key, default=None):
        # We reroute through __getitem__ and __setitem__, skipping _next
        try:
            return self[key]
        except KeyError:
            self[key] = default
            return default


class AsAttrAccess(Part):
    implements(IAsAttrAccess)

    @default
    def as_attribute_access(self):
        return AttributeAccess(self)


class ChildFactory(Part):
    implements(IChildFactory)
    factories = default(odict())
    
    @extend
    def __iter__(self):
        return self.factories.__iter__()
    
    iterkeys = extend(__iter__)
    
    @plumb
    def __getitem__(_next, self, key):
        try:
            child = _next(self, key)
        except KeyError:
            child = self.factories[key]()
            self[key] = child
        return child


class FixedChildren(Part):
    """Part that initializes a fixed dictionary as children

    The children are instantiated during __init__ and adopted by the
    class using this part. They cannot receive init argumentes, but
    could retrieve configuration from their parent.
    
    XXX: This implementation is similar to what's implemented in
         cone.app.model.FactoryNode. harmonize.
    """
    implements(IFixedChildren)
    fixed_children_factories = default(None)

    @plumb
    def __init__(_next, self, *args, **kw):
        _next(self, *args, **kw)
        self._children = odict()
        for key, factory in self.fixed_children_factories:
            child = factory()
            child.__name__ = key
            child.__parent__ = self
            self._children[key] = child

    @finalize
    def __delitem__(self, key):
        raise NotImplementedError("read-only")

    @finalize
    def __getitem__(self, key):
        return self._children[key]

    @finalize
    def __iter__(self):
        return iter(self._children)

    @finalize
    def __setitem__(self, key, val):
        raise NotImplementedError("read-only")


class GetattrChildren(Part):
    """Access children via ``__getattr__``, given the attribute name is unused.
    
    XXX: Similar behavior as AsAttrAccess. harmonize.
    """
    implements(IGetattrChildren)
    
    @finalize
    def __getattr__(self, name):
        """For new-style classes __getattr__ is called, if the
        attribute could not be found via MRO
        """
        return self.__getitem__(name)


class NodeChildValidate(Part):
    implements(INodeChildValidate)

    allow_non_node_childs = default(False)

    @plumb
    def __setitem__(_next, self, key, val):
        if not self.allow_non_node_childs and inspect.isclass(val):
            raise ValueError, u"It isn't allowed to use classes as values."
        if not self.allow_non_node_childs and not INode.providedBy(val):
            raise ValueError("Non-node childs are not allowed.")
        _next(self, key, val)


class UnicodeAware(Part):
    # XXX: It feels here it would be nice to be able to get an instance of a
    # plumbing to configure the codec.
    implements(IUnicodeAware)

    @plumb
    def __delitem__(_next, self, key):
        if isinstance(key, str):
            key = decode(key)
        _next(self, key)

    @plumb
    def __getitem__(_next, self, key):
        if isinstance(key, str):
            key = decode(key)
        return _next(self, key)

    @plumb
    def __setitem__(_next, self, key, val):
        if isinstance(key, str):
            key = decode(key)
        if isinstance(val, str):
            val = decode(val)
        return _next(self, key, val)


class UUIDAware(Part):
    implements(IUUIDAware)
    
    uuid = default(None)
    overwrite_recursiv_on_copy = default(True)
    
    @plumb
    def __init__(_next, self, *args, **kw):
        _next(self, *args, **kw)
        self.uuid = uuid.uuid4()
    
    @plumb
    def copy(_next, self):
        copied = _next(self)
        self.set_uuid_for(copied, True, self.overwrite_recursiv_on_copy)
        return copied
    
    @default
    def set_uuid_for(self, node, override=False, recursiv=False):
        if IUUIDAware.providedBy(node):
            if override or not node.uuid:
                node.uuid = uuid.uuid4()
        if recursiv:
            for child in node.values():
                self.set_uuid_for(child, override, recursiv)

#class Wrap(Part):
#    """Plumbing element that wraps nodes coming from deeper levels in a
#    NodeNode.
#    """
#    implements(IWrap)
#
#    @plumb
#    def __getitem__(_next, self, key):
#        val = _next(self, key)
#        if INode.providedBy(val):
#            val = NodeNode(val)
#        return val
#
#    @plumb
#    def __setitem__(_next, self, key, val):
#        if INode.providedBy(val):
#            val = val.context
#        _next(self, key, val)
