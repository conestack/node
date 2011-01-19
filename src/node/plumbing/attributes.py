from plumber import (
    plumb,
    extend,
    default,
)
from zope.interface import implements
from node.interfaces import IAttributed
from node.base import OrderedNode
from node.utils import AttributeAccess


class NodeAttributes(OrderedNode):
    
    def __init__(self, context):
        OrderedNode.__init__(self)
        self.allow_non_node_childs = True
        self.context = context
        self._node = context # BBB
    
    def __repr__(self):
        name = unicode(self.__parent__.__name__).encode('ascii', 'replace')
        return "<%s object '%s' at %s>" % (self.__class__.__name__,
                                           name,
                                           hex(id(self))[:-1])


class Attributes(object):
    
    implements(IAttributed)
    
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
