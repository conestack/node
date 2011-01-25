from plumber import plumber

from node.parts.mapping import FullMapping
from node.parts.nodify import Nodify
from node.utils import (
    AttributeAccess,
    LocationIterator,
)


class _ImplMixin(object):
    """Abstract mixin class for different node implementations.

    A class utilizing this contract must inherit from choosen ``IFullMaping``.

    We cannot use same contract as in ``odict.odict`` -> ``_dict_impl``.
    Odict requires the dict implementation to store it's internal double linked
    list while we need to have an implementation which must provide a ready to
    use ``IFullMapping``
    """

    def _mapping_impl(self):
        """Return ``IFullMaping`` implementing class.
        """
        raise NotImplementedError
