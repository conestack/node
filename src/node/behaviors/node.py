from __future__ import absolute_import
from node.compat import IS_PY2
from node.interfaces import IContentishNode
from node.interfaces import IDefaultInit
from node.interfaces import IMappingNode
from node.interfaces import INode
from node.interfaces import INodeInit
from node.interfaces import IOrdered
from node.interfaces import ISchemaProperties
from node.interfaces import ISequenceNode
from node.utils import LocationIterator
from node.utils import safe_decode
from plumber import Behavior
from plumber import default
from plumber import override
from plumber import plumb
from zope.interface import implementer
from zope.interface.interfaces import IInterface


@implementer(IDefaultInit)
class DefaultInit(Behavior):

    @override
    def __init__(self, name=None, parent=None):
        self.__name__ = name
        self.__parent__ = parent


@implementer(INodeInit)
class NodeInit(Behavior):

    @plumb
    def __init__(next_, self, *args, **kwargs):
        self.__name__ = kwargs.pop('name', None)
        self.__parent__ = kwargs.pop('parent', None)
        next_(self, *args, **kwargs)


@implementer(INode)
class Node(Behavior):
    __name__ = default(None)
    __parent__ = default(None)

    @override
    @property
    def name(self):
        return self.__name__

    @override
    @property
    def parent(self):
        return self.__parent__

    @override
    @property
    def path(self):
        path = [parent.name for parent in LocationIterator(self)]
        path.reverse()
        return path

    @override
    @property
    def root(self):
        root = None
        for parent in LocationIterator(self):
            root = parent
        return root

    @override
    def acquire(self, interface):
        node = self.parent
        while node:
            if (
                (
                    IInterface.providedBy(interface)
                    and interface.providedBy(node)
                )
                or isinstance(node, interface)
            ):
                return node
            node = node.parent

    @default
    def __nonzero__(self):
        return True

    __bool__ = default(__nonzero__)

    @override
    def __repr__(self):
        class_name = self.__class__.__name__
        name = self.name.encode('ascii', 'replace') \
            if IS_PY2 and isinstance(self.name, unicode) \
            else str(self.name)
        return '<{} object \'{}\' at {}>'.format(
            class_name,
            name,
            hex(id(self))[:-1]
        )

    __str__ = override(__repr__)

    @override
    @property
    def noderepr(self):
        """``noderepr`` is used in ``treerepr``.

        Thus, we can overwrite it in subclass and return any debug information
        we need while ``__repr__`` is an enhanced standard object
        representation, also used as ``__str__`` on nodes.
        """
        class_name = self.__class__
        name = self.name.encode('ascii', 'replace') \
            if IS_PY2 and isinstance(self.name, unicode) \
            else str(self.name)
        return str(class_name) + ': ' + name[name.find(':') + 1:]

    @override
    def treerepr(self, indent=0, prefix=' '):
        res = '{}{}\n'.format(indent * prefix, self.noderepr)
        children = list()
        schema_members = set()
        if ISchemaProperties.providedBy(self):
            def collect_schema_members(cls):
                for schema_member in getattr(cls, '__schema_members__', []):
                    schema_members.add(schema_member)
                for base in cls.__bases__:
                    collect_schema_members(base)
            collect_schema_members(self.__class__)
            children += sorted([
                (name, getattr(self, name))
                for name in schema_members
            ], key=lambda x: x[0])
        if IMappingNode.providedBy(self):
            items = (
                self.items()
                if IOrdered.providedBy(self)
                else sorted(self.items(), key=lambda x: safe_decode(x[0]))
            )
            for item in items:
                if item[0] not in schema_members:
                    children.append(item)
        elif ISequenceNode.providedBy(self):
            children += [(index, value) for index, value in enumerate(self)]
        for name, value in children:
            if INode.providedBy(value):
                res += value.treerepr(indent=indent + 2, prefix=prefix)
            else:
                res += '{}{}: {}\n'.format(
                    (indent + 2) * prefix,
                    name,
                    repr(value)
                )
        return res

    @override
    def printtree(self):
        print(self.treerepr())                               # pragma: no cover


@implementer(IContentishNode)
class ContentishNode(Node):

    @override
    def detach(self, name):
        node = self[name]
        del self[name]
        node.__parent__ = None
        return node
