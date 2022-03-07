from __future__ import absolute_import
from node.interfaces import IConstraints
from node.interfaces import IMappingConstraints
from node.interfaces import INode
from node.interfaces import ISequenceConstraints
from plumber import Behavior
from plumber import default
from plumber import plumb
from zope.interface import implementer
from zope.interface.interfaces import IInterface
import warnings


def child_constraints(node):
    if hasattr(node, 'allow_non_node_childs'):
        warnings.warn(
            '``allow_non_node_childs`` is deprecated, '
            'use ``child_constraints`` instead'
        )
        constraints = tuple() if node.allow_non_node_childs else (INode,)
    elif hasattr(node, 'allow_non_node_children'):
        warnings.warn(
            '``allow_non_node_children`` is deprecated, '
            'use ``child_constraints`` instead'
        )
        constraints = tuple() if node.allow_non_node_children else (INode,)
    else:
        constraints = node.child_constraints
        constraints = constraints if constraints else tuple()
    return constraints


def check_constraints(node, value):
    for constraint in child_constraints(node):
        if IInterface.providedBy(constraint):
            if not constraint.providedBy(value):
                raise ValueError(
                    'Given value does not implement {}'.format(constraint)
                )
        elif not isinstance(value, constraint):
            raise ValueError(
                'Given value is no instance of {}'.format(constraint.__name__)
            )


@implementer(IConstraints)
class Constraints(Behavior):
    child_constraints = default((INode,))


@implementer(IMappingConstraints)
class MappingConstraints(Constraints):

    @plumb
    def __setitem__(next_, self, key, value):
        check_constraints(self, value)
        next_(self, key, value)


@implementer(ISequenceConstraints)
class SequenceConstraints(Constraints):

    @plumb
    def __setitem__(next_, self, index, value):
        check_constraints(self, value)
        next_(self, index, value)

    @plumb
    def insert(next_, self, index, value):
        check_constraints(self, value)
        next_(self, index, value)
