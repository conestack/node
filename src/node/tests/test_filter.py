from node.behaviors import DictStorage
from node.behaviors import ListStorage
from node.behaviors import MappingFilter
from node.behaviors import MappingNode
from node.behaviors import NodeInit
from node.behaviors import SequenceFilter
from node.behaviors import SequenceNode
from node.interfaces import IChildFilter
from plumber import plumbing
import unittest


@plumbing(
    NodeInit,
    MappingNode,
    MappingFilter,
    DictStorage)
class FilterMappingNode(object):
    pass


@plumbing(
    NodeInit,
    SequenceNode,
    SequenceFilter,
    ListStorage)
class FilterSequenceNode(object):
    pass


class TestFilter(unittest.TestCase):

    def test_MappingFilter(self):
        node = FilterMappingNode()
        node_1 = node['1'] = FilterMappingNode()
        node_2 = node['2'] = FilterSequenceNode()

        self.assertEqual(node.filtered_children(FilterMappingNode), [node_1])
        self.assertEqual(
            node.filtered_children(IChildFilter),
            [node_1, node_2]
        )

    def test_SequenceFilter(self):
        node = FilterSequenceNode()
        node_1 = FilterMappingNode()
        node_2 = FilterSequenceNode()
        node.append(node_1)
        node.append(node_2)

        self.assertEqual(node.filtered_children(FilterMappingNode), [node_1])
        self.assertEqual(
            node.filtered_children(IChildFilter),
            [node_1, node_2]
        )
