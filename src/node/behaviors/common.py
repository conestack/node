from __future__ import absolute_import
from node.interfaces import IAsAttrAccess
from node.interfaces import IUnicodeAware
from node.interfaces import IUUIDAware
from node.utils import AttributeAccess
from node.utils import decode
from plumber import Behavior
from plumber import default
from plumber import plumb
from zope.interface import implementer
import uuid


@implementer(IAsAttrAccess)
class AsAttrAccess(Behavior):

    @default
    def as_attribute_access(self):
        return AttributeAccess(self)


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
        if not self.uuid:
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
