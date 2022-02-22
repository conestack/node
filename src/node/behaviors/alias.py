from __future__ import absolute_import
from node.interfaces import IAlias
from node.interfaces import IAliaser
from node.utils import ReverseMapping
from odict import odict
from plumber import Behavior
from plumber import default
from plumber import plumb
from zope.interface import implementer
from zope.interface.common.mapping import IEnumerableMapping
from zope.interface.common.mapping import IFullMapping


@implementer(IAliaser, IFullMapping)
class DictAliaser(odict):
    """Uses its own dictionary for aliasing.

    ``__getitem__`` -> unalias
    """

    def __init__(self, data=(), strict=True):
        super(DictAliaser, self).__init__(data)
        self.strict = strict

    def alias(self, key):
        try:
            return ReverseMapping(self)[key]
        except KeyError as e:
            if not self.strict:
                return key
            raise e

    def unalias(self, aliased_key):
        try:
            return self[aliased_key]
        except KeyError as e:
            if not self.strict:
                return aliased_key
            raise e


@implementer(IAliaser)
class PrefixAliaser(object):
    """An aliaser that prefix all keys.

    As it never raise KeyError it is not whitelisting.
    """

    def __init__(self, prefix=None):
        self.prefix = prefix

    def alias(self, key):
        return (self.prefix or '') + key

    def unalias(self, prefixed_key):
        """Returns the real key for a prefixed_key."""
        prefix = self.prefix or ''
        if not prefixed_key.startswith(prefix):
            raise KeyError(u"key '{}' does not match prefix '{}'".format(
                prefixed_key,
                prefix
            ))
        return prefixed_key[len(prefix):]


@implementer(IAliaser)
class SuffixAliaser(object):
    """An aliaser that suffixes all keys.

    As it never raise KeyError it is not whitelisting.
    """

    def __init__(self, suffix=None):
        self.suffix = suffix

    def alias(self, key):
        return key + (self.suffix or '')

    def unalias(self, suffixed_key):
        """returns the real key for a suffixed_key."""
        suffix = self.suffix or ''
        if not suffixed_key.endswith(suffix):
            raise KeyError(u"key '{}' does not match suffix '{}'".format(
                suffixed_key,
                suffix
            ))
        return suffixed_key[:-len(suffix)]


@implementer(IAliaser)
class AliaserChain(object):
    """A chain of aliasers.

    chain = [aliaser1, aliaser2]
    chain.alias(key) == aliaser2.alias(aliaser1.alias(key))
    chain.unalias(alias_key) == aliaser2.unalias(aliaser1.unalias(aliased_key))
    """

    def __init__(self, chain=None):
        self.chain = chain

    def alias(self, key):
        for aliaser in self.chain:
            key = aliaser.alias(key)
        return key

    def unalias(self, key):
        for aliaser in reversed(self.chain):
            key = aliaser.unalias(key)
        return key


class PrefixSuffixAliaser(AliaserChain):
    """Prefixes and suffixes."""

    def __init__(self, prefix=None, suffix=None):
        self.chain = (PrefixAliaser(prefix), SuffixAliaser(suffix))


@implementer(IAlias)
class Alias(Behavior):
    aliaser = default(None)

    @plumb
    def __getitem__(next_, self, key):
        if self.aliaser:
            unaliased_key = self.aliaser.unalias(key)
        else:
            unaliased_key = key
        try:
            return next_(self, unaliased_key)
        except KeyError:
            raise KeyError(key)

    @plumb
    def __setitem__(next_, self, key, val):
        if self.aliaser:
            unaliased_key = self.aliaser.unalias(key)
        else:
            unaliased_key = key
        try:
            next_(self, unaliased_key, val)
        except KeyError:
            raise KeyError(key)

    @plumb
    def __delitem__(next_, self, key):
        if self.aliaser:
            unaliased_key = self.aliaser.unalias(key)
        else:
            unaliased_key = key
        try:
            next_(self, unaliased_key)
        except KeyError:
            raise KeyError(key)

    @plumb
    def __iter__(next_, self):
        for key in next_(self):
            try:
                if self.aliaser:
                    yield self.aliaser.alias(key)
                else:
                    yield key
            except KeyError:
                if IEnumerableMapping.providedBy(self.aliaser):
                    # an enumerable aliaser whitelists, we skip non-listed keys
                    continue
                raise
