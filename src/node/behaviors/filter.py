from __future__ import absolute_import
from node.interfaces import IChildFilter
from plumber import Behavior
from plumber import default
from zope.interface import implementer
from zope.interface.interfaces import IInterface


def filter_objects(objects, filter):
    if IInterface.providedBy(filter):
        return [ob for ob in objects if filter.providedBy(ob)]
    else:
        return [ob for ob in objects if isinstance(ob, filter)]


@implementer(IChildFilter)
class MappingFilter(Behavior):

    @default
    def filtered_children(self, filter):
        return filter_objects(self.values(), filter)


@implementer(IChildFilter)
class SequenceFilter(Behavior):

    @default
    def filtered_children(self, filter):
        return filter_objects(self, filter)
