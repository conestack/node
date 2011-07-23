from plumber import (
    plumber,
    plumb,
    finalize,
    default,
    Part,
)
from node.interfaces import IAttributes
from node.parts.common import (
    Adopt,
    NodeChildValidate,
)
from node.parts.nodify import Nodify
from node.parts.storage import OdictStorage
from node.utils import AttributeAccess
from zope.interface import implements


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
        self.context = parent # BBB 2011-01-31
        self._node = parent   # BBB 2011-01-31
    
    # XXX: do we need that or could we make normal nodes show their parent,
    # too?
    def __repr__(self):
        name = unicode(self.parent.name).encode('ascii', 'replace')
        return "<%s object '%s' at %s>" % (self.__class__.__name__,
                                           name,
                                           hex(id(self))[:-1])


# XXX: inherit from nodespaces part
class Attributes(Part):
    implements(IAttributes)
    
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
