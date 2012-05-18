from odict import odict
from plumber import (
    plumber,
    default,
    plumb,
    Part,
)
from zope.interface import implementer
from zope.interface.common.mapping import (
    IEnumerableMapping,
    IFullMapping,
)
from node.interfaces import IAliaser
from node.interfaces import IAlias
from node.utils import ReverseMapping

# XXX: remove
from node.parts.common import Adopt, NodeChildValidate
from node.parts.nodify import Nodify



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
        """Returns the real key for a prefixed_key.
        """
        prefix = self.prefix or ''
        if not prefixed_key.startswith(prefix):
            raise KeyError(u"key '%s' does not match prefix '%s'" % \
                    (prefixed_key, prefix))
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
        """returns the real key for a suffixed_key
        """
        suffix = self.suffix or ''
        if not suffixed_key.endswith(suffix):
            raise KeyError(
                    u"key '%s' does not match suffix '%s'" % \
                            (suffixed_key, suffix)
                    )
        return suffixed_key[:-len(suffix)]


@implementer(IAliaser)
class AliaserChain(object):
    """A chain of aliasers.

    chain = [aliaser1, aliaser2]
    chain.alias(key) == aliaser2.alias(aliaser1.alias(key))
    chain.unalias(alias_key) == aliaser2.unalias(aliaser1.unalias(aliased_key))
    """
    
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


@implementer(IAlias)
class Alias(Part):
    """KeyErrors are caught and reraised with the aliased key.
    XXX: Could be configureable: aliased_keyerrors.

    XXX: Problem: at least __contains__, keys and iterkeys would also need to
    be aliased, or made sure that they are based on the methods aliased here.
    This could be ensured by the end point. However, end points in general
    might want to provide more efficient implementations for let's say
    __contains__. Leaving this open until we experience it.

    One way to handle it would be a way for plumbing elements to reroute method
    calls on themselves. However, this would mask methods on deeper levels and
    would need to be made explicit. For the Alias element the best approach is
    probably to just implement plumbing methods independently for all methods
    necessary - however, it's tedious, e.g. for iteritems.

    For rerouting we would needs entrance methods, see below in commented
    iteritems.
    """
    aliaser = default(None)
    
    @plumb
    def __init__(_next, self, *args, **kw):
        if 'aliaser' in kw:
            self.aliaser = kw.pop('aliaser')
        _next(self, *args, **kw)

    @plumb
    def __delitem__(_next, self, key):
        if self.aliaser:
            unaliased_key = self.aliaser.unalias(key)
        else:
            unaliased_key = key
        try:
            _next(self, unaliased_key)
        except KeyError:
            raise KeyError(key)

    @plumb
    def __getitem__(_next, self, key):
        if self.aliaser:
            unaliased_key = self.aliaser.unalias(key)
        else:
            unaliased_key = key
        try:
            return _next(self, unaliased_key)
        except KeyError:
            raise KeyError(key)

    @plumb
    def __iter__(_next, self):
        for key in _next(self):
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

    @plumb
    def __setitem__(_next, self, key, val):
        if self.aliaser:
            unaliased_key = self.aliaser.unalias(key)
        else:
            unaliased_key = key
        try:
            _next(self, unaliased_key, val)
        except KeyError:
            raise KeyError(key)

#    @plumb
#    def iteritems(_next, self):
#        """XXX non-functional
#
#        idea is to ignore _next, but instead reroute to other functions here
#
#        However, whose __getitem__ to use? entrance at the very beginning?
#        There might be somebody playing with __getitem__ and definitely wants
#        those items not items from here.
#        """
#        for key in entrance('__iter__', pipe_starting_from_here)(self):
#            ...
#            XXX: and now, the __getitem__ from here, or the one from the
#            beginning?
#
#   As we are at it, whose __getitem__ is used, if a non-plumbing method from
#   the end point uses __getitem__
#
#   It is clear if we just do self[key] --> entrance at the beginning
#   the same for: for key in self:
#
#   However, it means, that behind Alias no iteritems will be used anymore,
#   which would mean that Alias needs to happen as late as possible and all
#   tempering with iteritems needs to happen earlier in the chain.
#
#   late -> back of the chain
#   early -> front of the chain
#