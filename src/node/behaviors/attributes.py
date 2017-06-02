# -*- coding: utf-8 -*-
from node.behaviors.common import Adopt
from node.behaviors.common import NodeChildValidate
from node.behaviors.nodify import Nodify
from node.behaviors.storage import OdictStorage
from node.compat import IS_PY2
from node.interfaces import IAttributes
from node.utils import AttributeAccess
from plumber import Behavior
from plumber import default
from plumber import finalize
from plumber import plumbing
from zope.interface import implementer


@plumbing(
    NodeChildValidate,
    Adopt,
    Nodify,
    OdictStorage)
class NodeAttributes(object):
    allow_non_node_childs = True

    def __init__(self, name=None, parent=None):
        self.__name__ = name
        self.__parent__ = parent
        self.context = parent  # B/C 2011-01-31
        self._node = parent    # B/C 2011-01-31

    def __repr__(self):
        name = self.parent.name.encode('ascii', 'replace') \
            if IS_PY2 and isinstance(self.parent.name, unicode) \
            else str(self.parent.name)
        return '<{} object \'{}\' at {}>'.format(
            self.__class__.__name__,
            name,
            hex(id(self))[:-1]
        )


@implementer(IAttributes)
class Attributes(Behavior):
    attribute_access_for_attrs = default(False)
    attributes_factory = default(NodeAttributes)

    @finalize
    @property
    def attrs(self):
        try:
            attrs = self.nodespaces['__attrs__']
        except KeyError:
            attrs = self.nodespaces['__attrs__'] = \
                self.attributes_factory(name='__attrs__', parent=self)
        if self.attribute_access_for_attrs:
            return AttributeAccess(attrs)
        return attrs

    # B/C
    attributes = finalize(attrs)
