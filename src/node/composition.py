# XXX: NEEDS UPDATE to plumbing

# XXX: used in zodict.

from zope.interface import implements
from odict import odict
from interfaces import IComposition
from bbb import Node

class Composition(Node):
    """
    A composition is a node that has one or more nodespaces that are the base for
    its child nodespace. A child has its own child nodespace and optionally
    arbitrary further named nodespaces, eg. 'attrs'.

    A composition can work in two general modes:
    - virtual children (composition is not child.__parent__), using its nodespaces
      as child factories
    - real children (composition is child.__parent__), that are compositions
      factored on the base of matching children from the nodespaces
    """
    implements(IComposition)

    def __init__(self, name=None, nodespaces=None):
        # XXX: index support turned off for now
        super(Composition, self).__init__(name=name, index=False)
        if nodespaces:
            # copy the nodespaces into our nodespace
            self.nodespaces.update(nodespaces)

    def _perform(self, funcstr, args, msg):
        """perform one of th actions __getitem__, __setitem__, __delitem

        ``args`` = (key, optional:val)
        """
        # The key needs to be aliased by the corresponding nodespaces aliaser
        for nkey in self.nodespaces:
            if nkey[:2] == nkey[-2:] == '__':
                # we skip internal ones
                continue
            try:
                try:
                    aliaser = self.aliaser[nkey]
                except (TypeError, KeyError):
                    aliaser = None
                ourkey = aliaser and aliaser.unalias(args[0]) or args[0]
                func = getattr(self.nodespaces[nkey], funcstr)
                ourargs = [ourkey] + list(args[1:])
                return func(*ourargs)
            except KeyError:
                continue
        raise KeyError(msg)

    def __getitem__(self, key):
        return self._perform(
                '__getitem__',
                (key,),
                u"No nodespace provided key %s" % (key,),
                )

    def __setitem__(self, key, val):
        return self._perform(
                '__setitem__',
                (key, val),
                u"No nodespace accepted key %s" % (key,),
                )

    def __delitem__(self, key):
        return self._perform(
                '__delitem__',
                (key,),
                u"No nodespace had key %s" % (key,),
                )
        
    def __iter__(self):
        # This iter uses the iter of its nodespaces
        buf = dict()
        for nkey in self.nodespaces:
            if nkey[:2] == nkey[-2:] == '__':
                # we skip internal ones
                continue
            nodespace = self.nodespaces[nkey]
            for key in nodespace:
                try:
                    buf[key]
                except KeyError:
                    buf[key] = None
                    yield key

    def iteritems(self):
        for key in self:
            yield key, self[key]

    def itervalues(self):
        for key in self:
            yield self[key]