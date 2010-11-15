#XXX: should we split this up into node.aliasing.interfaces?
# Benefit: the structure would be the same as for modules provided by separate
# distributions
from zope.interface import Interface


class IAliaser(Interface):
    """Generic Aliasing Interface
    """
    def alias(key):
        """returns the alias for a key
        """

    def unalias(aliased_key):
        """returns the key belonging to an aliased_key
        """
