from __future__ import absolute_import
from node.interfaces import IChildFactory
from node.interfaces import IFixedChildren
from odict import odict
from plumber import Behavior
from plumber import default
from plumber import finalize
from plumber import override
from plumber import plumb
from zope.interface import implementer
import warnings


@implementer(IChildFactory)
class ChildFactory(Behavior):
    factories = default(odict())

    @override
    def __iter__(self):
        return self.factories.__iter__()

    iterkeys = override(__iter__)

    @plumb
    def __getitem__(next_, self, key):
        try:
            child = next_(self, key)
        except KeyError:
            factory = self.factories[key]
            try:
                child = factory(name=key, parent=self)
            except TypeError:
                warnings.warn(
                    'Calling child factory without arguments is deprecated. '
                    'Adopt your factoriy to accept ``name`` and ``parent``.'
                )
                child = factory()
            self[key] = child
        return child


@implementer(IFixedChildren)
class FixedChildren(Behavior):
    """Behavior that initializes a fixed dictionary as children.

    The children are instantiated during __init__.
    """
    factories = default(odict())

    @plumb
    def __init__(next_, self, *args, **kw):
        next_(self, *args, **kw)
        self._children = odict()
        if hasattr(self, 'fixed_children_factories'):
            warnings.warn(
                '``fixed_children_factories`` is deprecated, '
                'use ``factories`` instead'
            )
            factories = self.fixed_children_factories
            # This is a B/C interface contract violation hack. The interface
            # describes the factories as dict, but prior to node 1.1 the
            # implementation expected a tuple or list
            factories = (
                odict(factories) if isinstance(factories, (list, tuple))
                else factories
            )
        else:
            factories = self.factories
        for key, factory in factories.items():
            try:
                child = factory(name=key, parent=self)
            except TypeError:
                warnings.warn(
                    'Calling child factory without arguments is deprecated. '
                    'Adopt your factoriy to accept ``name`` and ``parent``.'
                )
                child = factory()
            child.__name__ = key
            child.__parent__ = self
            self._children[key] = child

    @finalize
    def __setitem__(self, key, val):
        raise NotImplementedError('read-only')

    @finalize
    def __getitem__(self, key):
        return self._children[key]

    @finalize
    def __delitem__(self, key):
        raise NotImplementedError('read-only')

    @finalize
    def __iter__(self):
        return iter(self._children)
