# -*- coding: utf-8 -*-
from node.interfaces import IAdopt
from node.interfaces import IAsAttrAccess
from node.interfaces import IChildFactory
from node.interfaces import IFixedChildren
from node.interfaces import IGetattrChildren
from node.interfaces import INode
from node.interfaces import INodeChildValidate
from node.interfaces import IUnicodeAware
from node.interfaces import IUUIDAware
from node.utils import AttributeAccess
from node.utils import decode
from odict import odict
from plumber import Behavior
from plumber import default
from plumber import finalize
from plumber import override
from plumber import plumb
from zope.interface import implementer
import inspect
import uuid


@implementer(IAdopt)
class Adopt(Behavior):

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


@implementer(IAsAttrAccess)
class AsAttrAccess(Behavior):

    @default
    def as_attribute_access(self):
        return AttributeAccess(self)


@implementer(IChildFactory)
class ChildFactory(Behavior):
    factories = default(odict())

    @override
    def __iter__(self):
        return self.factories.__iter__()

    iterkeys = override(__iter__)

    @plumb
    def __getitem__(_next, self, key):
        try:
            child = _next(self, key)
        except KeyError:
            child = self.factories[key]()
            self[key] = child
        return child


@implementer(IFixedChildren)
class FixedChildren(Behavior):
    """Behavior that initializes a fixed dictionary as children

    The children are instantiated during __init__ and adopted by the
    class using this behavior. They cannot receive init argumentes, but
    could retrieve configuration from their parent.

    XXX: This implementation is similar to what's implemented in
         cone.app.model.FactoryNode. harmonize.
    """
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
        raise NotImplementedError('read-only')

    @finalize
    def __getitem__(self, key):
        return self._children[key]

    @finalize
    def __iter__(self):
        return iter(self._children)

    @finalize
    def __setitem__(self, key, val):
        raise NotImplementedError('read-only')


@implementer(IGetattrChildren)
class GetattrChildren(Behavior):
    """Access children via ``__getattr__``, given the attribute name is unused.

    XXX: Similar behavior as ``AsAttrAccess``. consolidate.
    """

    @finalize
    def __getattr__(self, name):
        """For new-style classes __getattr__ is called, if the
        attribute could not be found via MRO
        """
        return self[name]


@implementer(INodeChildValidate)
class NodeChildValidate(Behavior):
    allow_non_node_childs = default(False)

    @plumb
    def __setitem__(_next, self, key, val):
        if not self.allow_non_node_childs and inspect.isclass(val):
            raise ValueError('It isn\'t allowed to use classes as values.')
        if not self.allow_non_node_childs and not INode.providedBy(val):
            raise ValueError('Non-node childs are not allowed.')
        _next(self, key, val)


@implementer(IUnicodeAware)
class UnicodeAware(Behavior):
    # XXX: It feels here it would be nice to be able to get an instance of a
    # plumbing to configure the codec.

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


@implementer(IUUIDAware)
class UUIDAware(Behavior):
    uuid = default(None)
    overwrite_recursiv_on_copy = default(True)

    @plumb
    def __init__(_next, self, *args, **kw):
        _next(self, *args, **kw)
        self.uuid = self.uuid_factory()

    @plumb
    def copy(_next, self):
        msg = 'Shallow copy useless on UUID aware node trees, use deepcopy.'
        raise RuntimeError(msg)

    @plumb
    def deepcopy(_next, self):
        copied = _next(self)
        self.set_uuid_for(copied, True, self.overwrite_recursiv_on_copy)
        return copied

    @default
    def uuid_factory(self):
        return uuid.uuid4()

    @default
    def set_uuid_for(self, node, override=False, recursiv=False):
        if IUUIDAware.providedBy(node):
            if override or not node.uuid:
                node.uuid = self.uuid_factory()
        if recursiv:
            for child in node.values():
                self.set_uuid_for(child, override, recursiv)
