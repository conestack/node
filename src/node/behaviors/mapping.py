import copy
from plumber import (
    Behavior,
    default,
)
from zope.interface import implementer
from zope.interface.common.mapping import (
    IItemMapping,
    IReadMapping,
    IIterableMapping,
    IWriteMapping,
    IEnumerableMapping,
    IMapping,
    IClonableMapping,
    IExtendedReadMapping,
    IExtendedWriteMapping,
    IFullMapping,
)
from ..utils import UNSET


@implementer(IItemMapping)
class ItemMapping(Behavior):
    """Simplest readable mapping object
    """

    @default
    def __getitem__(self, key):
        raise NotImplementedError


@implementer(IReadMapping)
class ReadMapping(ItemMapping):
    """Basic mapping interface
    """

    @default
    def get(self, key, default=None):
        """Uses ``__getitem__``.
        """
        try:
            return self[key]
        except KeyError:
            return default

    @default
    def __contains__(self, key):
        """Uses ``__getitem__``.

        This should be overriden by storages (using override), where
        ``__getitem__`` is expensive.

        XXX: also catching the exception is expensive, so this should be
        overriden probably always.
        """
        try:
            self[key]
        except KeyError:
            return False
        return True


@implementer(IWriteMapping)
class WriteMapping(Behavior):
    """Mapping methods for changing data
    """

    @default
    def __delitem__(self, key):
        raise NotImplementedError

    @default
    def __setitem__(self, key, value):
        raise NotImplementedError


@implementer(IEnumerableMapping)
class EnumerableMapping(ReadMapping):
    """Mapping objects whose items can be enumerated.
    """

    @default
    def keys(self):
        """Uses ``__iter__``.
        """
        return [x for x in self]

    @default
    def __iter__(self):
        raise NotImplementedError

    @default
    def values(self):
        """Uses ``__iter__`` and ``__getitem__``.

        return values in key order
        """
        return [self[key] for key in self]

    @default
    def items(self):
        """Uses ``__iter__`` and ``__getitem__``.

        return items in key order
        """
        return [(key, self[key]) for key in self]

    @default
    def __len__(self):
        """Uses ``keys``.
        """
        return len(self.keys())


@implementer(IMapping)
class Mapping(WriteMapping, EnumerableMapping):
    """Simple mapping interface
    """


@implementer(IIterableMapping)
class IterableMapping(EnumerableMapping):

    @default
    def iterkeys(self):
        """Uses ``__iter__``.
        """
        return self.__iter__()

    @default
    def itervalues(self):
        """Uses ``__iter__`` and ``__getitem__``.

        iter values in key order
        """
        for key in self:
            yield self[key]

    @default
    def iteritems(self):
        """Uses ``__iter__`` and ``__getitem__``.

        iter items in key order
        """
        for key in self:
            yield key, self[key]


@implementer(IClonableMapping)
class ClonableMapping(Behavior):

    @default
    def copy(self):
        return copy.copy(self)

    @default
    def deepcopy(self):
        # not part of IClonableMapping API
        return copy.deepcopy(self)


@implementer(IExtendedReadMapping)
class ExtendedReadMapping(IterableMapping):

    @default
    def has_key(self, key):
        """uses ``__iter__``
        """
        return key in self


@implementer(IExtendedWriteMapping)
class ExtendedWriteMapping(WriteMapping):

    @default
    def clear(self):
        """works only if together with EnumerableMapping
        """
        for key in self.keys():
            del self[key]

    @default
    def update(self, *args, **kw):
        if len(args) > 1:
            raise TypeError("At most one positional argument, not: %s." % \
                    (len(args),))
        if args:
            data = args[0]
            if hasattr(data, 'iteritems'):
                data = data.iteritems()
            for key, val in data:
                self[key] = val
        for key, val in kw.iteritems():
            self[key] = val

    @default
    def setdefault(self, key, default=None):
        """works only if together with ReadMapping
        """
        try:
            return self[key]
        except KeyError:
            self[key] = default
            return default

    @default
    def pop(self, key, default=UNSET):
        """works only if together with ReadMapping
        """
        try:
            val = self[key]
            del self[key]
        except KeyError:
            if default is UNSET:
                raise
            val = default
        return val

    @default
    def popitem(self):
        """works only if together with IterableMapping
        """
        for key in reversed(self.keys()):
            val = self[key]
            del self[key]
            return key, val
        raise KeyError('popitem(): mapping is empty')


@implementer(IFullMapping)
class FullMapping(ExtendedReadMapping,
                  ExtendedWriteMapping,
                  ClonableMapping,
                  Mapping):
    """Provides defaults for IFullMapping

    NotImplementedError is raised by defaults for:
        - ``__delitem__``
        - ``__getitem__``
        - ``__iter__``
        - ``__setitem__``
    """
