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
import fnmatch
import itertools
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
                    'Adopt your factory to accept ``name`` and ``parent``.'
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
    # https://man7.org/linux/man-pages/man7/glob.7.html
    chars = asterisks = question_marks = sequences = 0
    in_sequence = 0
    for char in pattern:
        if not in_sequence and char == '[':
            in_sequence += 1
            continue
        if in_sequence:
            if in_sequence < 2 or char != ']':
                in_sequence += 1
                continue
            else:
                in_sequence = 0
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
    """Simple wildcard pattern weighting.

    Limitations:
        * Sequences are not weighted.
        * Max 100 sequences in pattern.
        * Max 100 question_marks in pattern.
        * Max 100 asterisks in pattern.

    If we want to have a proper weighting of all pattern aspects, we'd need to
    view patterns as finite state machines and count all required states
    necessary to resolve the pattern. This count can then be used as weight.
    https://github.com/adrian-thurston/ragel might be a starting point if we
    somewhen want to implement this.
    """
    specificities = [
        [],  # patterns with no wildcards
        [],  # patterns with sequences
        [],  # patterns with sequences and question marks
        []   # patterns with all wildcards
    ]
    weights = dict()
    for pattern in patterns:
        (
            chars,
            asterisks,
            question_marks,
            sequences
        ) = _wildcard_pattern_occurrences(pattern)
        weights[pattern] = (
            0 - chars +
            sequences / 1000000. +
            question_marks / 10000. +
            asterisks / 100.
        )
        # patterns with no wildcards
        if asterisks + question_marks + sequences == 0:
            specificities[0].append(pattern)
        # patterns with sequences
        elif asterisks + question_marks == 0:
            specificities[1].append(pattern)
        # patterns with sequences and question marks
        elif asterisks == 0:
            specificities[2].append(pattern)
        # patterns with all wildcards
        else:
            specificities[3].append(pattern)
    return tuple(itertools.chain.from_iterable([
        sorted(specificity, key=lambda x: weights[x])
        for specificity in specificities
    ]))


@implementer(IWildcardFactory)
class WildcardFactory(Behavior):
    factories = default(odict())
    pattern_weighting = default(True)

    @default
    def factory_for_pattern(self, name):
        factories = self.factories
        patterns = (
            _wildcard_patterns_by_specificity(tuple(factories))
            if self.pattern_weighting
            else factories
        )
        for pattern in patterns:
            if fnmatch.fnmatchcase(name, pattern):
                return factories[pattern]
