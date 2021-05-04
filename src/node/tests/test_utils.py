# -*- coding: utf-8 -*-
from node.base import BaseNode
from node.tests import NodeTestCase
from node.utils import AttributeAccess
from node.utils import debug
from node.utils import decode
from node.utils import encode
from node.utils import instance_property
from node.utils import logger
from node.utils import node_by_path
from node.utils import ReverseMapping
from node.utils import safe_decode
from node.utils import safe_encode
from node.utils import StrCodec
from node.utils import UNSET
from odict import odict
import logging


class TestUtils(NodeTestCase):

    def test_UNSET(self):
        self.assertEqual(repr(UNSET), '<UNSET>')
        self.assertEqual(str(UNSET), '')
        self.assertFalse(bool(UNSET))
        self.assertEqual(len(UNSET), 0)

    def test_ReverseMapping(self):
        context = odict([
            ('foo', 'a'),
            ('bar', 'b')
        ])
        mapping = ReverseMapping(context)
        self.assertEqual([v for v in mapping], ['a', 'b'])
        self.assertEqual(mapping.keys(), ['a', 'b'])
        self.assertEqual(mapping.values(), ['foo', 'bar'])
        self.assertEqual(mapping.items(), [('a', 'foo'), ('b', 'bar')])
        self.assertEqual(len(mapping), 2)
        self.assertTrue('a' in mapping)
        self.assertFalse('foo' in mapping)
        self.assertEqual(mapping['a'], 'foo')
        err = self.expectError(KeyError, lambda: mapping['foo'])
        self.assertEqual(str(err), '\'foo\'')
        self.assertEqual(mapping.get('b'), 'bar')
        self.assertEqual(mapping.get('foo', 'DEFAULT'), 'DEFAULT')

    def test_AttributeAccess(self):
        context = odict([
            ('foo', 'a'),
            ('bar', 'b')
        ])
        attraccess = AttributeAccess(context)
        self.assertEqual(attraccess.foo, 'a')
        err = self.expectError(AttributeError, lambda: attraccess.a)
        self.assertEqual(str(err), 'a')
        attraccess.foo = 'foo'
        self.assertEqual(attraccess.foo, 'foo')
        self.assertEqual(attraccess['foo'], 'foo')
        attraccess['baz'] = 'bla'
        self.assertEqual(attraccess.baz, 'bla')
        del attraccess['bar']
        self.assertEqual(
            object.__getattribute__(attraccess, 'context').keys(),
            ['foo', 'baz']
        )
        attraccess.x = 0
        self.assertEqual(
            object.__getattribute__(attraccess, 'context').keys(),
            ['foo', 'baz', 'x']
        )

    def test_encode(self):
        self.assertEqual(
            encode(
                b'\x01\x05\x00\x00\x00\x00\x00\x05\x15\x00\x00\x00\xd4'
                b'\xa0\xff\xff\xaeW\x82\xa9P\xcf8\xaf&\x0e\x00\x00'
            ), (
                b'\x01\x05\x00\x00\x00\x00\x00\x05\x15\x00\x00\x00\xd4'
                b'\xa0\xff\xff\xaeW\x82\xa9P\xcf8\xaf&\x0e\x00\x00'
            )
        )
        self.assertEqual(encode(u'\xe4'), b'\xc3\xa4')
        self.assertEqual(encode([u'\xe4']), [b'\xc3\xa4'])
        self.assertEqual(
            encode({u'\xe4': u'\xe4'}),
            {b'\xc3\xa4': b'\xc3\xa4'}
        )
        self.assertEqual(encode(b'\xc3\xa4'), b'\xc3\xa4')

        node = BaseNode()
        node.allow_non_node_childs = True
        node['foo'] = u'\xe4'
        self.assertEqual(encode(node), {b'foo': b'\xc3\xa4'})

    def test_decode(self):
        self.assertEqual(decode(b'foo'), u'foo')
        self.assertEqual(decode((b'foo', u'bar')), (u'foo', u'bar'))
        self.assertEqual(decode({b'foo': b'bar'}), {u'foo': u'bar'})
        self.assertEqual(decode(b'fo\xe4'), b'fo\xe4')

        node = BaseNode()
        node.allow_non_node_childs = True
        node[b'foo'] = b'\xc3\xa4'
        self.assertEqual(decode(node), {u'foo': u'\xe4'})

    def test_StrCodec(self):
        codec = StrCodec(soft=False)
        expected = (
            'codec can\'t decode byte 0xe4 in position 2: '
            'unexpected end of data'
        )
        err = self.expectError(UnicodeDecodeError,
                               lambda: codec.decode(b'fo\xe4'))
        self.assertTrue(str(err).find(expected) > -1)

    def test_safe_encode(self):
        self.assertEqual(safe_encode(u'äöü'), b'\xc3\xa4\xc3\xb6\xc3\xbc')
        self.assertEqual(safe_encode(b'already_string'), b'already_string')

    def test_safe_decode(self):
        self.assertEqual(safe_decode(b'\xc3\xa4\xc3\xb6\xc3\xbc'), u'äöü')
        self.assertEqual(safe_decode(u'already_unicode'), u'already_unicode')

    def test_instance_property(self):
        computed = list()

        class InstancePropertyTest(object):

            @instance_property
            def property(self):
                computed.append('Computed')
                return 'value'

        obj = InstancePropertyTest()
        expected = '\'InstancePropertyTest\' object has no attribute ' \
                   '\'_property\''
        err = self.expectError(AttributeError, lambda: obj._property)
        self.assertEqual(str(err), expected)

        self.assertEqual(obj.property, 'value')
        self.assertEqual(computed, ['Computed'])
        computed = list()

        self.assertEqual(obj._property, 'value')

        self.assertEqual(obj.property, 'value')
        self.assertEqual(computed, [])

    def test_node_by_path(self):
        root = BaseNode(name='root')
        child = root['child'] = BaseNode()
        sub = child['sub'] = BaseNode()

        self.assertEqual(node_by_path(root, ''), root)
        self.assertEqual(node_by_path(root, '/'), root)
        self.assertEqual(node_by_path(root, []), root)

        self.assertEqual(node_by_path(root, 'child'), child)
        self.assertEqual(node_by_path(root, '/child'), child)

        self.assertEqual(node_by_path(root, 'child/sub'), sub)

        self.assertEqual(node_by_path(root, ['child']), child)

        self.assertEqual(node_by_path(root, ['child', 'sub']), sub)

        class CustomPathIterator(object):
            def __iter__(self):
                yield 'child'
                yield 'sub'

        self.assertEqual(node_by_path(root, CustomPathIterator()), sub)

    def test_debug_helper(self):
        messages = list()

        class TestHandler(logging.StreamHandler):
            def handle(self, record):
                messages.append(str(record))

        handler = TestHandler()
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

        @debug
        def test_search(a, b=42):
            pass

        test_search(21)

        self.assertTrue(str(messages[0]).find('LogRecord: node, 10,') > -1)
        self.assertTrue(str(messages[0]).find('utils.py') > -1)
        self.assertTrue(str(messages[0]).find('"test_search: args=(21,), kws={}">') > -1)

        self.assertTrue(str(messages[1]).find('LogRecord: node, 10,') > -1)
        self.assertTrue(str(messages[1]).find('utils.py') > -1)
        self.assertTrue(str(messages[1]).find('"test_search: --> None">') > -1)

        logger.setLevel(logging.INFO)
        logger.removeHandler(handler)
