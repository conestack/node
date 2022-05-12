from __future__ import absolute_import
from node.compat import lru_cache
from node.interfaces import IChildFactory
from node.interfaces import IFixedChildren
from node.interfaces import IWildcardFactory
from odict import odict
from plumber import Behavior
from plumber import default
from plumber import finalize
from plumber import override
from plumber import plumb
from zope.interface import implementer
import warnings


@implementer(IChildFactory)
class ChildFactory(Behavior):
    factories = default(odict())

    @override
    def __iter__(self):
        return self.factories.__iter__()

    iterkeys = override(__iter__)

    @plumb
    def __getitem__(next_, self, key):
        try:
            child = next_(self, key)
        except KeyError:
            factory = self.factories[key]
            try:
                child = factory(name=key, parent=self)
            except TypeError:
                warnings.warn(
                    'Calling child factory without arguments is deprecated. '
                    'Adopt your factoriy to accept ``name`` and ``parent``.'
                )
                child = factory()
            self[key] = child
        return child


@implementer(IFixedChildren)
class FixedChildren(Behavior):
    """Behavior that initializes a fixed dictionary as children.

    The children are instantiated during __init__.
    """
    factories = default(odict())

    @plumb
    def __init__(next_, self, *args, **kw):
        next_(self, *args, **kw)
        self._children = odict()
        if hasattr(self, 'fixed_children_factories'):
            warnings.warn(
                '``fixed_children_factories`` is deprecated, '
                'use ``factories`` instead'
            )
            factories = self.fixed_children_factories
            # This is a B/C interface contract violation hack. The interface
            # describes the factories as dict, but prior to node 1.1 the
            # implementation expected a tuple or list
            factories = (
                odict(factories) if isinstance(factories, (list, tuple))
                else factories
            )
        else:
            factories = self.factories
        for key, factory in factories.items():
            try:
                child = factory(name=key, parent=self)
            except TypeError:
                warnings.warn(
                    'Calling child factory without arguments is deprecated. '
                    'Adopt your factoriy to accept ``name`` and ``parent``.'
                )
                child = factory()
            child.__name__ = key
            child.__parent__ = self
            self._children[key] = child

    @finalize
    def __setitem__(self, key, val):
        raise NotImplementedError('read-only')

    @finalize
    def __getitem__(self, key):
        return self._children[key]

    @finalize
    def __delitem__(self, key):
        raise NotImplementedError('read-only')

    @finalize
    def __iter__(self):
        return iter(self._children)


@lru_cache(maxsize=32768)
def _wildcard_pattern_occurrences(pattern):
    # count characters, asterisks, question_marks and sequences in pattern
    # a whole sequencs counts as one character
    chars = asterisks = question_marks = sequences = 0
    in_sequence = False
    for char in pattern:
        if char == '[':
            in_sequence = True
            continue
        if in_sequence:
            if char != ']':
                continue
            else:
                in_sequence = False
                sequences += 1
        if char == '*':
            asterisks += 1
        elif char == '?':
            question_marks += 1
        chars += 1
    if in_sequence:
        raise ValueError('Pattern contains non-closing sequence')
    return chars, asterisks, question_marks, sequences


@lru_cache(maxsize=32768)
def _wildcard_patterns_by_specificity(patterns):
    # limitations:
    #   * sequences are not weighted
    #   * max 100 sequences in pattern
    #   * max 100 question_marks in pattern
    #   * max 100 asterisks in pattern
    specificity_1 = []  # patterns with no wildcards
    specificity_2 = []  # patterns with sequences only
    specificity_3 = []  # patterns with sequences and question marks
    specificity_4 = []  # patterns with sequences, question marks and asterisks
    weights = dict()
    for pattern in patterns:
        (
            chars, asterisks, question_marks, sequences
        ) = _wildcard_pattern_occurrences(pattern)
        weights[pattern] = (
            0 - chars - sequences * .01 -
            question_marks * .0001 - asterisks * .000001
        )
        if asterisks + question_marks + sequences == 0:
            specificity_1.append(pattern)
        elif asterisks + question_marks == 0:
            specificity_2.append(pattern)
        elif asterisks == 0:
            specificity_3.append(pattern)
        else:
            specificity_4.append(pattern)
    return tuple(
        sorted(specificity_1, key=lambda x: weights[x]) +
        sorted(specificity_2, key=lambda x: weights[x]) +
        sorted(specificity_3, key=lambda x: weights[x]) +
        sorted(specificity_4, key=lambda x: weights[x])
    )


@implementer(IWildcardFactory)
class WildcardFactory(Behavior):
    factories = default(odict())

    def factory_for_name(self, name):
        """"""
