import logging
from zope.interface import implementer
from zope.interface.common.mapping import IEnumerableMapping
from interfaces import (
    IAttributeAccess,
    INode,
)


logger = logging.getLogger('node')


class Unset(object):
    """Used to identify unset values in contrast to None.

    use for example by node.behaviors.nodify.Nodify.
    """

    def __nonzero__(self):
        return False

    def __str__(self):
        return ''

    def __len__(self):
        return 0

    def __repr__(self):
        return '<UNSET>'


UNSET = Unset()


def LocationIterator(object):
    """Iterate over an object and all of its parents.

    Copied from ``zope.location.LocationIterator``.

    """
    while object is not None:
        yield object
        object = getattr(object, '__parent__', None)


@implementer(IEnumerableMapping)
class ReverseMapping(object):
    """Reversed IEnumerableMapping.
    """

    def __init__(self, context):
        """Object behaves as adapter for dict like object.

        ``context``: a dict like object.
        """
        self.context = context

    def __getitem__(self, value):
        for key in self.context:
            if self.context[key] == value:
                return key
        raise KeyError(value)

    def get(self, value, default=None):
        try:
            return self[value]
        except KeyError:
            return default

    def __contains__(self, value):
        for key in self.context:
            val = self.context[key]
            if val == value:
                return True
        return False

    def keys(self):
        return [val for val in self]

    def __iter__(self):
        for key in self.context:
            yield self.context[key]

    def values(self):
        return [key for key in self.context]

    def items(self):
        return [(v, k) for k, v in self.context.items()]

    def __len__(self):
        return len(self.context)


@implementer(IAttributeAccess)
class AttributeAccess(object):
    """If someone really needs to access the original context (which should
    not happen), she hast to use ``object.__getattr__(attraccess, 'context')``.
    """

    def __init__(self, context):
        object.__setattr__(self, 'context', context)

    def __getattr__(self, name):
        context = object.__getattribute__(self, 'context')
        try:
            return context[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        context = object.__getattribute__(self, 'context')
        context[name] = value

    def __getitem__(self, name):
        context = object.__getattribute__(self, 'context')
        return context[name]

    def __setitem__(self, name, value):
        context = object.__getattribute__(self, 'context')
        context[name] = value

    def __delitem__(self, name):
        context = object.__getattribute__(self, 'context')
        del context[name]


CHARACTER_ENCODING = 'utf-8'


class StrCodec(object):
    """Encode unicodes to strs and decode strs to unicodes

    We will recursively work on arbitrarily nested structures consisting of
    str, unicode, list, tuple, dict and INode implementations mixed with
    others, which we won't touch. During that process a deep copy is produces
    leaving the orginal data structure intact.
    """

    def __init__(self, encoding=CHARACTER_ENCODING, soft=True):
        """
        ``encoding``
            the character encoding to decode from/encode to

        ``soft``
           if True, catch UnicodeDecodeErrors and leave this strings as-is.
        """
        self._encoding = encoding
        self._soft = soft

    def encode(self, arg):
        """Return an encoded copy of the argument

        - strs are decoded and reencode to make sure they conform to the
          encoding.
          XXX: makes no sence, especially because a UnicodeDecodeError ends up
               in a recursion error due to re-trying to encode. See below.
               Added condition to return if str is still str after decoding.
               This behavior should be removed completely.

        - unicodes are encoded as str according to encoding

        - lists/tuples/dicts are recursively worked on

        - everything else is left untouched
        """
        if isinstance(arg, (list, tuple)):
            arg = arg.__class__(map(self.encode, arg))
        elif isinstance(arg, dict):
            arg = dict([self.encode(t) for t in arg.iteritems()])
        elif isinstance(arg, str):
            arg = self.decode(arg)
            # If UnicodeDecodeError, binary data is expected. Return value
            # as is.
            if not isinstance(arg, str):
                arg = self.encode(arg)
        elif isinstance(arg, unicode):
            arg = arg.encode(self._encoding)
        elif INode.providedBy(arg):
            arg = dict([self.encode(t) for t in arg.iteritems()])
        return arg

    def decode(self, arg):
        if isinstance(arg, (list, tuple)):
            arg = arg.__class__(map(self.decode, arg))
        elif isinstance(arg, dict):
            arg = dict([self.decode(t) for t in arg.iteritems()])
        elif isinstance(arg, str):
            try:
                arg = arg.decode(self._encoding)
            except UnicodeDecodeError:
                # in soft mode we leave the string, otherwise we raise the
                # exception
                if not self._soft:
                    raise
        elif INode.providedBy(arg):
            arg = dict([self.decode(t) for t in arg.iteritems()])
        return arg


strcodec = StrCodec()
encode = strcodec.encode
decode = strcodec.decode


def instance_property(func):
    """Decorator like ``property``, but underlying function is only called once
    per instance.

    Set instance attribute with '_' prefix.
    """
    def wrapper(self):
        attribute_name = '_%s' % func.__name__
        if not hasattr(self, attribute_name):
            setattr(self, attribute_name, func(self))
        return getattr(self, attribute_name)
    wrapper.__doc__ = func.__doc__
    return property(wrapper)


def debug(func):
    """Decorator for logging debug messages.
    """
    def wrapped(*args, **kws):
        logger.debug(
            u'%s: args=%s, kws=%s' % (
                func.func_name, unicode(args), unicode(kws)))
        f_result = func(*args, **kws)
        logger.debug(u'%s: --> %s' % (func.func_name, unicode(f_result)))
        return f_result
    wrapped.__doc__ = func.__doc__
    return wrapped
