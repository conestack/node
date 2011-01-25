from plumber import (
    default,
    Part,
)
from node.interfaces import IAsAttrAccess
from node.utils import AttributeAccess
from zope.interface import implements


class AsAttrAccess(Part):
    implements(IAsAttrAccess)
    
    @default
    def as_attribute_access(self):
        return AttributeAccess(self)