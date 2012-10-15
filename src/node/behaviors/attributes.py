from plumber import (
    plumber,
    finalize,
    default,
    Behavior,
)
from zope.interface import implementer
from ..interfaces import IAttributes
from ..utils import AttributeAccess
from .common import (
    Adopt,
    NodeChildValidate,
)
from .nodify import Nodify
from .storage import OdictStorage


class NodeAttributes(object):
    __metaclass__ = plumber
    __plumbing__ = (
        NodeChildValidate,
        Adopt,
        Nodify,
        OdictStorage,
    )
    allow_non_node_childs = True

    def __init__(self, name=None, parent=None):
        self.__name__ = name
        self.__parent__ = parent
        self.context = parent  # BBB 2011-01-31
        self._node = parent    # BBB 2011-01-31

    def __repr__(self):
        name = unicode(self.parent.name).encode('ascii', 'replace')
        return "<%s object '%s' at %s>" % (self.__class__.__name__,
                                           name,
                                           hex(id(self))[:-1])


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

    # BBB
    attributes = finalize(attrs)
