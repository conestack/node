from zope.interface import implements
from node.interfaces import IAttributed
from node.base import OrderedNode
from node.meta import (
    behavior,
    BaseBehavior,
)
from node.utils import AttributeAccess


class NodeAttributes(OrderedNode):
    
    def __init__(self, context):
        OrderedNode.__init__(self)
        self.allow_non_node_childs = True
        self.context = context
        # BBB
        self._node = context
    
    def __repr__(self):
        name = unicode(self.__parent__.__name__).encode('ascii', 'replace')
        return "<%s object '%s' at %s>" % (self.__class__.__name__,
                                           name,
                                           hex(id(self))[:-1])


class Attributed(BaseBehavior):
    implements(IAttributed)
    
    attribute_access_for_attrs = False
    
    attributes_factory = NodeAttributes
    
    expose_write_access_for = [
        'attribute_access_for_attrs',
        'attributes_factory',
    ]
    
    def __init__(self, context):
        super(Attributed, self).__init__(context)
    
    @property
    def attrs(self):
        try:
            attrs = self.context.nodespaces['__attrs__']
        except KeyError:
            attrs = self.context.nodespaces['__attrs__'] = \
                self.attributes_factory(self)
            attrs.__name__ = '__attrs__'
            attrs.__parent__ = self.context
        if self.attribute_access_for_attrs:
            return AttributeAccess(attrs)
        return attrs
    
    # BBB
    attributes = attrs
