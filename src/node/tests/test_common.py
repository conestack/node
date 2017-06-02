from node.base import BaseNode
from node.behaviors import Adopt
from node.behaviors import ChildFactory
from node.behaviors import DefaultInit
from node.behaviors import FixedChildren
from node.behaviors import GetattrChildren
from node.behaviors import NodeChildValidate
from node.behaviors import Nodify
from node.behaviors import OdictStorage
from node.behaviors import UUIDAware
from node.behaviors import UnicodeAware
from node.testing.env import MockupNode
from node.testing.env import NoNode
from node.tests import NodeTestCase
from plumber import plumbing
import uuid


class TestCommon(NodeTestCase):

    def test_Adopt(self):
        # A dictionary is used as end point
        @plumbing(Adopt)
        class AdoptingDict(dict):
            pass

        ad = AdoptingDict()

        # The mockup node is adopted
        node = MockupNode()
        ad['foo'] = node
        self.assertTrue(ad['foo'] is node)
        self.assertEqual(node.__name__, 'foo')
        self.assertTrue(node.__parent__ is ad)

        # The non-node object is not adopted
        nonode = NoNode()
        ad['bar'] = nonode
        self.assertTrue(ad['bar'] is nonode)
        self.assertFalse(hasattr(nonode, '__name__'))
        self.assertFalse(hasattr(nonode, '__parent__'))

        # If something goes wrong, the adoption does not happen.
        # See ``plumbing.Adopt`` for exceptions that are handled.

        # XXX: In case this should be configurable, it would be nice if a
        # plumbing element could be instatiated which is currently not
        # possible. It would be possible by defining the plumbing __init__
        # method with a different name. Maybe it is also possible to have
        # two __init__ one decorated one not, if the plumbing decorator could
        # influence that all plumbing functions are stored under a different
        # name. If the decorator cannot do that a Plumbing metaclass will
        # work for sure, however, it is questionable whether it justifies a
        # metaclass instead of just naming the plumbing init
        # e.g. plumbing__init__

        class FakeDict(object):
            def __setitem__(self, key, val):
                raise KeyError(key)

            def setdefault(self, key, default=None):
                pass                                         # pragma: no cover

        @plumbing(Adopt)
        class FailingAD(FakeDict):
            pass

        fail = FailingAD()
        node = MockupNode()

        def __setitem_fails():
            fail['foo'] = node
        err = self.expect_error(KeyError, __setitem_fails)
        self.assertEqual(str(err), "'foo'")
        self.assertTrue(node.__name__ is None)
        self.assertTrue(node.__parent__ is None)

    def test_UnicodeAware(self):
        @plumbing(Nodify, UnicodeAware, OdictStorage)
        class UnicodeNode(object):
            pass

        node = UnicodeNode()
        node['foo'] = UnicodeNode()
        self.assertEqual(list(node.keys()), [u'foo'])

        node['bar'] = 'bar'
        self.assertEqual(
            node.items(),
            [(u'foo', node['foo']), (u'bar', u'bar')]
        )

        self.assertTrue(isinstance(node['foo'], UnicodeNode))

        del node['bar']
        self.assertEqual(list(node.keys()), [u'foo'])

    def test_ChildFactory(self):
        class FooChild(object):
            pass

        class BarChild(object):
            pass

        @plumbing(Nodify, ChildFactory, OdictStorage)
        class ChildFactoryNode(object):
            factories = {
                'foo': FooChild,
                'bar': BarChild,
            }

        node = ChildFactoryNode()
        self.check_output("""\
        [('bar', <...BarChild object at ...>),
        ('foo', <...FooChild object at ...>)]
        """, str(sorted(node.items())))

    def test_FixedChildren(self):
        class FooChild(object):
            pass

        class BarChild(object):
            pass

        @plumbing(Nodify, FixedChildren)
        class FixedChildrenNode(object):
            fixed_children_factories = (
                ('foo', FooChild),
                ('bar', BarChild),
                )

        node = FixedChildrenNode()
        self.assertEqual(list(node.keys()), ['foo', 'bar'])
        self.assertTrue(isinstance(node['foo'], FooChild))
        self.assertTrue(isinstance(node['bar'], BarChild))
        self.assertTrue(node['foo'] is node['foo'])

        def __delitem__fails():
            del node['foo']
        err = self.expect_error(NotImplementedError, __delitem__fails)
        self.assertEqual(str(err), 'read-only')

        def __setitem__fails():
            node['foo'] = 'foo'
        err = self.expect_error(NotImplementedError, __setitem__fails)
        self.assertEqual(str(err), 'read-only')

    def test_UUIDAware(self):
        # Create a uid aware node. ``copy`` is not supported on UUIDAware node
        # trees, ``deepcopy`` must be used
        @plumbing(
            Adopt,
            DefaultInit,
            Nodify,
            OdictStorage,
            UUIDAware)
        class UUIDNode(object):
            pass

        # UUID is set at init time
        root = UUIDNode(name='root')
        self.assertTrue(isinstance(root.uuid, uuid.UUID))

        # Shallow ``copy`` is prohibited for UUID aware nodes
        err = self.expect_error(RuntimeError, root.copy)
        exp = 'Shallow copy useless on UUID aware node trees, use deepcopy.'
        self.assertEqual(str(err), exp)

        # On ``deepcopy``, a new uid gets set:
        root_cp = root.deepcopy()
        self.assertFalse(root is root_cp)
        self.assertFalse(root.uuid == root_cp.uuid)

        # Create children, copy tree and check if all uuids have changed
        c1 = root['c1'] = UUIDNode()
        c1['s1'] = UUIDNode()
        self.assertEqual(root.treerepr(), (
            "<class 'node.tests.test_common.UUIDNode'>: root\n"
            "  <class 'node.tests.test_common.UUIDNode'>: c1\n"
            "    <class 'node.tests.test_common.UUIDNode'>: s1\n"
        ))

        root_cp = root.deepcopy()
        self.assertEqual(root_cp.treerepr(), (
            "<class 'node.tests.test_common.UUIDNode'>: root\n"
            "  <class 'node.tests.test_common.UUIDNode'>: c1\n"
            "    <class 'node.tests.test_common.UUIDNode'>: s1\n"
        ))

        self.assertFalse(root.uuid == root_cp.uuid)
        self.assertFalse(root['c1'].uuid == root_cp['c1'].uuid)
        self.assertFalse(root['c1']['s1'].uuid == root_cp['c1']['s1'].uuid)

        # When detaching part of a tree, uid's are not changed
        c1_uid = root['c1'].uuid
        s1_uid = root['c1']['s1'].uuid
        detached = root.detach('c1')

        self.assertEqual(root.treerepr(), (
            "<class 'node.tests.test_common.UUIDNode'>: root\n"
        ))

        self.assertEqual(detached.treerepr(), (
            "<class 'node.tests.test_common.UUIDNode'>: c1\n"
            "  <class 'node.tests.test_common.UUIDNode'>: s1\n"
        ))

        self.assertTrue(c1_uid == detached.uuid)
        self.assertTrue(s1_uid == detached['s1'].uuid)

    def test_NodeChildValidate(self):
        @plumbing(NodeChildValidate, DefaultInit, Nodify, OdictStorage)
        class NodeChildValidateNode(object):
            pass

        node = NodeChildValidateNode()
        self.assertFalse(node.allow_non_node_childs)

        def __setitem__fails():
            node['child'] = 1
        err = self.expect_error(ValueError, __setitem__fails)
        self.assertEqual(str(err), 'Non-node childs are not allowed.')

        class SomeClass(object):
            pass

        def __setitem__fails2():
            node['aclasshere'] = SomeClass
        err = self.expect_error(ValueError, __setitem__fails2)
        expected = "It isn't allowed to use classes as values."
        self.assertEqual(str(err), expected)

        node.allow_non_node_childs = True
        node['child'] = 1
        self.assertEqual(node['child'], 1)

    def test_GetattrChildren(self):
        # XXX: this test breaks coverage recording!!!:
        class GetattrBase(BaseNode):
            allow_non_node_childs = True
            baseattr = 1

        @plumbing(GetattrChildren)
        class GetattrNode(GetattrBase):
            ourattr = 2

        node = GetattrNode()
        node['foo'] = 10
        node['baseattr'] = 20
        node['ourattr'] = 30

        self.assertEqual(node['foo'], 10)
        self.assertEqual(node['baseattr'], 20)
        self.assertEqual(node['ourattr'], 30)

        # Only children not shadowed by real attributes can be accessed via
        # getattr
        self.assertEqual(node.foo, 10)
        self.assertEqual(node.baseattr, 1)
        self.assertEqual(node.ourattr, 2)
