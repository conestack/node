from plumber import plumbing
from zope.interface.common.mapping import IEnumerableMapping

from node.interfaces import INode


class Adopt(object):
    """Plumbing element that provides adoption of children
    """
    @plumbing
    def __setitem__(cls, _next, self, key, val):
        # only care about adopting if we have a node
        if not INode.providedBy(val):
            _next(self, key, val)
            return

        # save old __parent__ and __name__ to restore if something goes wrong
        old_name = val.__name__
        old_parent = val.__parent__
        val.__name__ = key
        val.__parent__ = self
        try:
            _next(self, key, val)
        except (AttributeError, KeyError, ValueError):
            # XXX: In what other cases do we want to revert adoption?
            val.__name__ = old_name
            val.__parent__ = old_parent
            raise


class Alias(object):
    """Plumbing element that provides aliasing of child names/keys

    KeyErrors are caught and reraised with the aliased key.
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
    iteritems
    """
    @plumbing
    def __init__(cls, _next, self, aliaser=None):
        self.aliaser = aliaser

    @plumbing
    def __delitem__(cls, _next, self, key):
        if self.aliaser:
            unaliased_key = self.aliaser.unalias(key)
        else:
            unaliased_key = key
        try:
            _next(self, unaliased_key)
        except KeyError:
            raise KeyError(key)

    @plumbing
    def __getitem__(cls, _next, self, key):
        if self.aliaser:
            unaliased_key = self.aliaser.unalias(key)
        else:
            unaliased_key = key
        try:
            return _next(self, unaliased_key)
        except KeyError:
            raise KeyError(key)

    @plumbing
    def __iter__(cls, _next, self):
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

    @plumbing
    def __setitem__(cls, _next, self, key, val):
        if self.aliaser:
            unaliased_key = self.aliaser.unalias(key)
        else:
            unaliased_key = key
        try:
            _next(self, unaliased_key, val)
        except KeyError:
            raise KeyError(key)

#    @plumbing
#    def iteritems(cls, _next, self):
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




# XXX: currently won't work, as the decode function is missing
# check the one in bda.ldap.strcodec
# XXX: It feels here it would be nice to be able to get an instance of a
# plumbing to configure the codec.
class Unicode(object):
    """Plumbing element to ensure unicode for keys and string values
    """
    @plumbing
    def __delitem__(cls, _next, self, key):
        if isinstance(key, str):
            key = decode(key)
        _next(key)

    @plumbing
    def __getitem__(cls, _next, self, key):
        if isinstance(key, str):
            key = decode(key)
        return _next(key)

    @plumbing
    def __setitem__(cls, _next, self, key, val):
        if isinstance(key, str):
            key = decode(key)
        if isinstance(val, str):
            val = decode(val)
        return _next(key, val)


class Wrap(object):
    """Plumbing element that wraps nodes coming from deeper levels in a NodeNode
    """
    @plumbing
    def __getitem__(cls, _next, self, key):
        val = _next(self, key)
        if INode.providedBy(val):
            val = NodeNode(val)
        return val

    @plumbing
    def __setitem__(cls, _next, self, key, val):
        if INode.providedBy(val):
            val = val.context
        _next(self, key, val)
