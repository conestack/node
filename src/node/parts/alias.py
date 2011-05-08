from plumber import (
    default,
    plumb,
    Part,
)
from node.interfaces import IAlias
from zope.interface import implements
from zope.interface.common.mapping import IEnumerableMapping


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
    implements(IAlias)
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
