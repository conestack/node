from plumber import default
from plumber import extend
from plumber import plumb
from plumber import Part
from zope.interface import implements

from node.interfaces import INode
from node.parts.mapping import FullMapping
from node.utils import Unset
from node.utils import LocationIterator
from node.utils import AttributeAccess


class Nodify(FullMapping):
    """Fills in gaps to implement full INode interface
    """
    implements(INode)
    __name__ = default(None)
    __parent__ = default(None)

    #@plumb
    #def __init__(_next, self, *args, **kw):
    #    # we have to pop our keywords before passing on, independent of when we
    #    # use then.
    #    name = kw.pop('name', Unset)
    #    parent = kw.pop('parent', Unset)

    #    # next in the chain
    #    _next(self, *args, **kw)

    #    # Set name and parent, if they were in kw
    #    if name is not Unset:
    #        self.__name__ = name
    #    if parent is not Unset:
    #        self.__parent__ = parent

    @plumb
    def copy(_next, self):
        new = _next(self)
        # XXX Where do we need a copy to have the same name, and when do we
        # need it to have the same parent? And what does it mean to have a
        # parent? Should be documented in Nodify doctest -cfl.
        new.__name__ = self.__name__
        new.__parent__ = self.__parent__
        return new
    
    @default
    @property
    def path(self):
        path = [parent.__name__ for parent in LocationIterator(self)]
        path.reverse()
        return path

    @default
    @property
    def root(self):
        root = None
        for parent in LocationIterator(self):
            root = parent
        return root

    @default
    def detach(self, key):
        node = self[key]
        del self[key]
        return node

    @default
    def filtereditervalues(self, interface):
        """Uses ``itervalues``.
        """
        for val in self.itervalues():
            if interface.providedBy(val):
                yield val

    @default
    def filteredvalues(self, interface):
        """Uses ``values``.
        """
        return [val for val in self.filtereditervalues(interface)]

    # BBB 2010-12-23
    filtereditems = default(filtereditervalues)

    # XXX: should be implemented by a wrapper like AliasedNodespace -cfl
    @default
    def as_attribute_access(self):
        return AttributeAccess(self)

    @default
    @property
    def noderepr(self):
        """``noderepr`` is used in ``printtree``.

        Thus, we can overwrite it in subclass and return any debug information
        we need while ``__repr__`` is an enhanced standard object
        representation, also used as ``__str__`` on nodes.

        XXX: do we really need the difference or can we just override __repr__
        in subclasses and use __repr__ in printtree?
        """
        if hasattr(self.__class__, '_wrapped'):
            class_ = self.__class__._wrapped
        else:
            class_ = self.__class__
        name = unicode(self.__name__).encode('ascii', 'replace')
        return str(class_) + ': ' + name[name.find(':') + 1:]

    @default
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


class NodeRepr(Part):

    @extend
    def __repr__(self):
        if hasattr(self.__class__, '_wrapped'):
            class_name = self.__class__._wrapped.__name__
        else:
            class_name = self.__class__.__name__
        # XXX: This is mainly used in doctest, I think
        #      doctest fails if we output utf-8
        name = unicode(self.__name__).encode('ascii', 'replace')
        return "<%s object '%s' at %s>" % (class_name,
                                           name,
                                           hex(id(self))[:-1])

    __str__ = extend(__repr__)
