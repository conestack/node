from __future__ import absolute_import
from node.compat import STR_TYPE
from node.interfaces import INodespaces
from odict import odict
from plumber import Behavior
from plumber import default
from plumber import finalize
from plumber import plumb
from zope.interface import implementer


@implementer(INodespaces)
class Nodespaces(Behavior):
    _nodespaces = default(None)

    @finalize
    @property
    def nodespaces(self):
        """A storage and general way to access our nodespaces.

        An ``AttributedNode`` uses this to store the ``attrs`` nodespace i.e.
        """
        if self._nodespaces is None:
            self._nodespaces = odict()
            self._nodespaces['__children__'] = self
        return self._nodespaces

    @plumb
    def __getitem__(next_, self, key):
        # blend in our nodespaces as children, with name __<name>__
        # isinstance check is required because odict tries to get item possibly
        # with ``_nil`` key, which is actually an object
        if isinstance(key, STR_TYPE) \
                and key.startswith('__') \
                and key.endswith('__'):
            # a reserved child key mapped to the nodespace behind
            # nodespaces[key], nodespaces is an odict
            return self.nodespaces[key]
        return next_(self, key)

    @plumb
    def __setitem__(next_, self, key, val):
        # blend in our nodespaces as children, with name __<name>__
        if key.startswith('__') and key.endswith('__'):
            # a reserved child key mapped to the nodespace behind
            # nodespaces[key], nodespaces is an odict
            val.__name__ = key
            val.__parent__ = self
            self.nodespaces[key] = val
            # index checks below must not happen for other nodespace.
            return
        next_(self, key, val)

    @plumb
    def __delitem__(next_, self, key):
        # blend in our nodespaces as children, with name __<name>__
        if key.startswith('__') and key.endswith('__'):
            # a reserved child key mapped to the nodespace behind
            # nodespaces[key], nodespaces is an odict
            del self.nodespaces[key]
            return
        next_(self, key)
