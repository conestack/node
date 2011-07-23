from odict import odict
from plumber import (
    plumber,
    Part,
)
from zope.interface import implements
from zope.interface.common.mapping import (
    IEnumerableMapping,
    IFullMapping,
)
from node.interfaces import IAliaser
from node.utils import ReverseMapping
from node.parts import (
    Adopt,
    Nodify,
    NodeChildValidate,
)


class DictAliaser(odict):
    """Uses its own dictionary for aliasing.

    ``__getitem__`` -> unalias
    """
    implements(IAliaser, IFullMapping)
    
    def __init__(self, data=(), strict=True):
        super(DictAliaser, self).__init__(data)
        self.strict = strict

    def alias(self, key):
        try:
            return ReverseMapping(self)[key]
        except KeyError, e:
            if not self.strict:
                return key
            raise e
    
    def unalias(self, aliased_key):
        try:
            return self[aliased_key]
        except KeyError, e:
            if not self.strict:
                return aliased_key
            raise e


class PrefixAliaser(object):
    """An aliaser that prefix all keys.

    As it never raise KeyError it is not whitelisting.
    """
    implements(IAliaser)

    def __init__(self, prefix=None):
        self.prefix = prefix

    def alias(self, key):
        return (self.prefix or '') + key

    def unalias(self, prefixed_key):
        """Returns the real key for a prefixed_key.
        """
        prefix = self.prefix or ''
        if not prefixed_key.startswith(prefix):
            raise KeyError(u"key '%s' does not match prefix '%s'" % \
                    (prefixed_key, prefix))
        return prefixed_key[len(prefix):]


class SuffixAliaser(object):
    """An aliaser that suffixes all keys.

    As it never raise KeyError it is not whitelisting.
    """
    implements(IAliaser)

    def __init__(self, suffix=None):
        self.suffix = suffix

    def alias(self, key):
        return key + (self.suffix or '')

    def unalias(self, suffixed_key):
        """returns the real key for a suffixed_key
        """
        suffix = self.suffix or ''
        if not suffixed_key.endswith(suffix):
            raise KeyError(
                    u"key '%s' does not match suffix '%s'" % \
                            (suffixed_key, suffix)
                    )
        return suffixed_key[:-len(suffix)]


class AliaserChain(object):
    """A chain of aliasers.

    chain = [aliaser1, aliaser2]
    chain.alias(key) == aliaser2.alias(aliaser1.alias(key))
    chain.unalias(alias_key) == aliaser2.unalias(aliaser1.unalias(aliased_key))
    """
    implements(IAliaser)
    
    # XXX: we are IEnumerableMapping if one of our childs is, which is
    #      important as we become a whitelist, eg. for Node.__iter__

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
    """Prefixes and suffixes.
    """
    
    def __init__(self, prefix=None, suffix=None):
        self.chain = (
            PrefixAliaser(prefix),
            SuffixAliaser(suffix))


#class NamedAliasers(dict):
#    """A dictionary storing aliasers by name.
#    
#    XXX
#    """


class AliasedNodespace(object):
    """Performs aliasing/unaliasing for node children.

    Is not the parent of its children, the children don't know about their name
    here.

    Future additional mode: children are wrapped, wrapper knows name and we are
    parent of wrapper.
    """
    __metaclass__ = plumber
    __plumbing__ = (
        NodeChildValidate,
        Adopt,
        Nodify,
    )
    
    def __init__(self, context, aliaser=None):
        """
        context
            the node whose children to alias
            
        aliaser
            the aliaser to be used
        """
        # XXX: is just taking over the name ok for all use cases? 
        # XXX: case where not? -rn
        #super(AliasedNodespace, self).__init__(context.name)
        
        self.__name__ = context.name
        self.__parent__ = None
        
        self.context = context
        self.aliaser = aliaser

    def __delitem__(self, key):
        unaliased_key = self.aliaser and self.aliaser.unalias(key) or key
        try:
            del self.context[unaliased_key]
        except KeyError:
            raise KeyError(key)

    def __getitem__(self, key):
        unaliased_key = self.aliaser and self.aliaser.unalias(key) or key
        try:
            return self.context[unaliased_key]
        except KeyError:
            raise KeyError(key)

    def __setitem__(self, key, val):
        unaliased_key = self.aliaser and self.aliaser.unalias(key) or key
        self.context[unaliased_key] = val
    
    def __iter__(self):
        for key in self.context:
            try:
                yield self.aliaser and self.aliaser.alias(key) or key
            except KeyError:
                if IEnumerableMapping.providedBy(self.aliaser):
                    # an enumerable aliaser whitelists, we skip non-listed keys
                    continue
                # no whitelisting and a KeyError on our internal data: that's
                # bad! Most probably not triggered on _Node but a subclass
                # XXX: test case showing this.
                raise RuntimeError(                         #pragma NO COVERAGE
                    u"Inconsist internal node state")       #pragma NO COVERAGE
    
    def __repr__(self):
        return "Aliased " + self.context.__repr__()