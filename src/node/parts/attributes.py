from plumber import (
    plumber,
    plumb,
    extend,
    default,
    Part,
)
from zope.interface import implements
from node.interfaces import IAttributes
from node.parts.common import (
    Adopt,
    NodeChildValidate,
)
from node.parts.nodify import Nodify
from node.parts.storage import OdictStorage
from node.utils import AttributeAccess


class NodeAttributes(object):
    
    __metaclass__ = plumber
    __plumbing__ = (
        NodeChildValidate,
        Adopt,
        Nodify,
        OdictStorage,
    )
    
    def __init__(self, context):
        self.allow_non_node_childs = True
        self.context = context
        self._node = context # BBB
    
    def __repr__(self):
        name = unicode(self.__parent__.__name__).encode('ascii', 'replace')
        return "<%s object '%s' at %s>" % (self.__class__.__name__,
                                           name,
                                           hex(id(self))[:-1])


class Attributes(Part):
    implements(IAttributes)
    
    attribute_access_for_attrs = default(False)
    attributes_factory = default(NodeAttributes)

    @extend
    @property
    def attrs(self):
        try:
            attrs = self.nodespaces['__attrs__']
        except KeyError:
            attrs = self.nodespaces['__attrs__'] = \
                self.attributes_factory(self)
            attrs.__name__ = '__attrs__'
            attrs.__parent__ = self
        if self.attribute_access_for_attrs:
            return AttributeAccess(attrs)
        return attrs
    
    # BBB
    attributes = extend(attrs)
