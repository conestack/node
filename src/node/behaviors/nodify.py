# -*- coding: utf-8 -*-
from __future__ import print_function
from node.behaviors.mapping import FullMapping
from node.compat import IS_PY2
from node.interfaces import IDefaultInit
from node.interfaces import IMappingNode
from node.interfaces import INode
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
    def detach(self, name):
        # XXX: maybe reset __name__ and __parent__ of detached node?
        node = self[name]
        del self[name]
        return node

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
        if ISchemaProperties.providedBy(self):
            children += sorted([
                (name, getattr(self, name))
                for name in self.__schema_members__
            ], key=lambda x: x[0])
        if IMappingNode.providedBy(self):
            children += self.items() \
                if IOrdered.providedBy(self) \
                else sorted(self.items(), key=lambda x: safe_decode(x[0]))
        elif ISequenceNode.providedBy(self):
            children += [(value.__name__, value) for value in self]
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


@implementer(IMappingNode)
class MappingNode(Node, FullMapping):

    @plumb
    def copy(_next, self):
        new = _next(self)
        new.__name__ = self.__name__
        new.__parent__ = self.__parent__
        return new

    @override
    def filtereditervalues(self, interface):
        for val in self.itervalues():
            if interface.providedBy(val):
                yield val

    @override
    def filteredvalues(self, interface):
        return [val for val in self.filtereditervalues(interface)]

    # B/C 2010-12-23
    filtereditems = override(filtereditervalues)


# B/C 2022-02-14
Nodify = MappingNode
