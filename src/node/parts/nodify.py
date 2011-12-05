from plumber import (
    default,
    extend,
    plumb,
    Part,
)
from zope.interface import implements
from zope.interface.interfaces import IInterface
from node.interfaces import (
    IDefaultInit,
    INodify,
)
from node.parts.mapping import FullMapping
from node.utils import (
    Unset,
    LocationIterator,
    AttributeAccess,
)


class DefaultInit(Part):
    implements(IDefaultInit)

    @extend
    def __init__(self, name=None, parent=None):
        self.__name__ = name
        self.__parent__ = parent


class Nodify(FullMapping):
    implements(INodify)
    __name__ = default(None)
    __parent__ = default(None)

    @plumb
    def copy(_next, self):
        new = _next(self)
        # XXX Where do we need a copy to have the same name, and when do we
        # need it to have the same parent? And what does it mean to have a
        # parent? Should be documented in Nodify doctest -cfl.
        new.__name__ = self.__name__
        new.__parent__ = self.__parent__
        return new

    @extend
    @property
    def name(self):
        return self.__name__

    @extend
    @property
    def parent(self):
        return self.__parent__

    @extend
    @property
    def path(self):
        path = [parent.name for parent in LocationIterator(self)]
        path.reverse()
        return path

    @extend
    @property
    def root(self):
        root = None
        for parent in LocationIterator(self):
            root = parent
        return root

    @extend
    def detach(self, key):
        node = self[key]
        del self[key]
        return node
    
    @extend
    def acquire(self, interface):
        node = self.parent
        while node:
            if (IInterface.providedBy(interface) \
              and interface.providedBy(node)) \
              or isinstance(node, interface):
                return node
            node = node.parent

    @extend
    def filtereditervalues(self, interface):
        """Uses ``itervalues``.
        """
        for val in self.itervalues():
            if interface.providedBy(val):
                yield val

    @extend
    def filteredvalues(self, interface):
        """Uses ``values``.
        """
        return [val for val in self.filtereditervalues(interface)]

    # BBB 2010-12-23
    filtereditems = extend(filtereditervalues)

    @extend
    @property
    def noderepr(self):
        """``noderepr`` is used in ``printtree``.

        Thus, we can overwrite it in subclass and return any debug information
        we need while ``__repr__`` is an enhanced standard object
        representation, also used as ``__str__`` on nodes.

        XXX: do we really need the difference or can we just override __repr__
        in subclasses and use __repr__ in printtree?
        """
        # XXX: is this a relict from plumber prototyping? -rn
        #if hasattr(self.__class__, '_wrapped'):
        #    class_ = self.__class__._wrapped
        #else:
        #    class_ = self.__class__
        class_ = self.__class__
        
        name = unicode(self.__name__).encode('ascii', 'replace')
        return str(class_) + ': ' + name[name.find(':') + 1:]

    @extend
    def printtree(self, indent=0):
        """Uses ``values``.
        """
        print "%s%s" % (indent * ' ', self.noderepr)
        for node in self.values():
            try:
                node.printtree(indent+2)
            except AttributeError:
                # Non-Node values are just printed
                print "%s%s" % (indent * ' ', node)

    # XXX: tricky one: If a base class provides a __nonzero__ and that
    # base class is nodified, should the base class' __nonzero__ be
    # used or this one? Please write your thoughts here -cfl
    # 
    # I think @default is fine, leaves most possible flexibility to the user.
    # Other thoughts? -rn
    @default
    def __nonzero__(self):
        return True

    @extend
    def __repr__(self):
        # XXX: is this a relict from plumber prototyping? -rn
        #if hasattr(self.__class__, '_wrapped'):
        #    class_name = self.__class__._wrapped.__name__
        #else:
        #    class_name = self.__class__.__name__
        class_name = self.__class__.__name__
        
        # XXX: This is mainly used in doctest, I think
        #      doctest fails if we output utf-8
        name = unicode(self.__name__).encode('ascii', 'replace')
        return "<%s object '%s' at %s>" % (class_name,
                                           name,
                                           hex(id(self))[:-1])

    __str__ = extend(__repr__)
