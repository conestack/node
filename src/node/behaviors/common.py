from __future__ import absolute_import
from node.interfaces import IAsAttrAccess
from node.interfaces import IChildFactory
from node.interfaces import IFixedChildren
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
import uuid


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
    def __getitem__(next_, self, key):
        try:
            child = next_(self, key)
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
         cone.app.model.FactoryNode. consolidate.
    """
    fixed_children_factories = default(None)

    @plumb
    def __init__(next_, self, *args, **kw):
        next_(self, *args, **kw)
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


@implementer(IUnicodeAware)
class UnicodeAware(Behavior):
    # XXX: It feels here it would be nice to be able to get an instance of a
    # plumbing to configure the codec.

    @plumb
    def __delitem__(next_, self, key):
        if isinstance(key, str):
            key = decode(key)
        next_(self, key)

    @plumb
    def __getitem__(next_, self, key):
        if isinstance(key, str):
            key = decode(key)
        return next_(self, key)

    @plumb
    def __setitem__(next_, self, key, val):
        if isinstance(key, str):
            key = decode(key)
        if isinstance(val, str):
            val = decode(val)
        return next_(self, key, val)


@implementer(IUUIDAware)
class UUIDAware(Behavior):
    uuid = default(None)
    overwrite_recursiv_on_copy = default(True)

    @plumb
    def __init__(next_, self, *args, **kw):
        next_(self, *args, **kw)
        self.uuid = self.uuid_factory()

    @plumb
    def copy(next_, self):
        msg = 'Shallow copy useless on UUID aware node trees, use deepcopy.'
        raise RuntimeError(msg)

    @plumb
    def deepcopy(next_, self):
        copied = next_(self)
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
