from __future__ import absolute_import
from node.interfaces import IBoundContext
from plumber import Behavior
from plumber import default
from zope.interface import implementer
from zope.interface.interfaces import IInterface
import inspect


@implementer(IBoundContext)
class BoundContext(Behavior):
    __bound_context_interfaces__ = default(())
    __bound_context_classes__ = default(())

    @default
    @classmethod
    def bind_context(cls, *context):
        if cls.__bound_context_interfaces__ + cls.__bound_context_classes__:
            raise RuntimeError('Class context already bound')
        interfaces = []
        classes = []
        for ob in context:
            if not ob:
                continue
            if IInterface.providedBy(ob):
                interfaces.append(ob)
            elif inspect.isclass(ob):
                classes.append(ob)
            else:
                raise ValueError('Context is neither an interface nor a class')
        cls.__bound_context_interfaces__ = tuple(interfaces)
        cls.__bound_context_classes__ = tuple(classes)

    @default
    def context_matches(self, obj):
        interfaces = self.__bound_context_interfaces__
        classes = self.__bound_context_classes__
        if not interfaces + classes:
            return True
        for interface in interfaces:
            if interface.providedBy(obj):
                return True
        for class_ in classes:
            if isinstance(obj, class_):
                return True
        return False
