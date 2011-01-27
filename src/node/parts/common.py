import inspect
from plumber import (
    default,
    plumb,
    Part,
)
from node.interfaces import (
    INode,
    IAdopt,
    IAsAttrAccess,
    IUnicode,
    INodeChildValidate,
    IWrap,
)
from node.utils import AttributeAccess
from zope.interface import implements


class Adopt(Part):
    """Plumbing element that provides adoption of children.
    """
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
        # We reroute through getitem and setitem, skipping _next
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


class Unicode(Part):
    """Plumbing element to ensure unicode for keys and string values.
    """
    # XXX: currently won't work, as the decode function is missing
    # check the one in bda.ldap.strcodec
    # XXX: It feels here it would be nice to be able to get an instance of a
    # plumbing to configure the codec.
    implements(IUnicode)
    
    @plumb
    def __delitem__(_next, self, key):
        if isinstance(key, str):
            key = decode(key)
        _next(key)

    @plumb
    def __getitem__(_next, self, key):
        if isinstance(key, str):
            key = decode(key)
        return _next(key)

    @plumb
    def __setitem__(_next, self, key, val):
        if isinstance(key, str):
            key = decode(key)
        if isinstance(val, str):
            val = decode(val)
        return _next(key, val)


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


class Wrap(Part):
    """Plumbing element that wraps nodes coming from deeper levels in a 
    NodeNode.
    """
    implements(IWrap)
    
    @plumb
    def __getitem__(_next, self, key):
        val = _next(self, key)
        if INode.providedBy(val):
            val = NodeNode(val)
        return val

    @plumb
    def __setitem__(_next, self, key, val):
        if INode.providedBy(val):
            val = val.context
        _next(self, key, val)
