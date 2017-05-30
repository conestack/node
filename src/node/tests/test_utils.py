from node.tests import NodeTestCase
from node.utils import AttributeAccess
from node.utils import ReverseMapping
from node.utils import UNSET
from odict import odict


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
        err = self.except_error(KeyError, lambda: mapping['foo'])
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
        err = self.except_error(AttributeError, lambda: attraccess.a)
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

"""

StrCodec decode and encode
--------------------------

.. code-block:: pycon

    >>> from node.base import BaseNode
    >>> from node.utils import StrCodec
    >>> from node.utils import encode
    >>> from node.utils import decode

    >>> encode('\x01\x05\x00\x00\x00\x00\x00\x05\x15\x00\x00\x00\xd4'
    ...        '\xa0\xff\xff\xaeW\x82\xa9P\xcf8\xaf&\x0e\x00\x00')
    '\x01\x05\x00\x00\x00\x00\x00\x05\x15\x00\x00\x00\xd4\xa0\xff\xff\xaeW\x82\xa9P\xcf8\xaf&\x0e\x00\x00'

    >>> encode(u'\xe4')
    '\xc3\xa4'

    >>> encode([u'\xe4'])
    ['\xc3\xa4']

    >>> encode({u'\xe4': u'\xe4'})
    {'\xc3\xa4': '\xc3\xa4'}

    >>> encode('\xc3\xa4')
    '\xc3\xa4'

    >>> node = BaseNode()
    >>> node.allow_non_node_childs = True
    >>> node['foo'] = u'\xe4'
    >>> encode(node)
    {'foo': '\xc3\xa4'}

    >>> decode('foo')
    u'foo'

    >>> decode(('foo', 'bar'))
    (u'foo', u'bar')

    >>> decode({'foo': 'bar'})
    {u'foo': u'bar'}

    >>> decode('fo\xe4')
    'fo\xe4'

    >>> node = BaseNode()
    >>> node.allow_non_node_childs = True
    >>> node['foo'] = '\xc3\xa4'
    >>> decode(node)
    {u'foo': u'\xe4'}

    >>> codec = StrCodec(soft=False)
    >>> codec.decode('fo\xe4')
    Traceback (most recent call last):
      ...
    UnicodeDecodeError: 'utf8' codec can't decode byte 0xe4 in position 2: 
    unexpected end of data


Instance property decorator
---------------------------

.. code-block:: pycon

    >>> from node.utils import instance_property

    >>> class InstancePropertyTest(object):
    ... 
    ...     @instance_property
    ...     def property(self):
    ...         print 'Computed only once'
    ...         return 'value'

    >>> obj = InstancePropertyTest()
    >>> obj._property
    Traceback (most recent call last):
      ...
    AttributeError: 'InstancePropertyTest' object has no attribute '_property'

    >>> obj.property
    Computed only once
    'value'

    >>> obj._property
    'value'

    >>> obj.property
    'value'


Node by path
------------

.. code-block:: pycon

    >>> from node.utils import node_by_path

    >>> root = BaseNode(name='root')
    >>> child = root['child'] = BaseNode()
    >>> sub = child['sub'] = BaseNode()

    >>> node_by_path(root, '')
    <BaseNode object 'root' at ...>

    >>> node_by_path(root, '/')
    <BaseNode object 'root' at ...>

    >>> node_by_path(root, [])
    <BaseNode object 'root' at ...>

    >>> node_by_path(root, 'child')
    <BaseNode object 'child' at ...>

    >>> node_by_path(root, '/child')
    <BaseNode object 'child' at ...>

    >>> node_by_path(root, 'child/sub')
    <BaseNode object 'sub' at ...>

    >>> node_by_path(root, ['child'])
    <BaseNode object 'child' at ...>

    >>> node_by_path(root, ['child', 'sub'])
    <BaseNode object 'sub' at ...>

    >>> class CustomPathIterator(object):
    ...     def __iter__(self):
    ...         yield 'child'
    ...         yield 'sub'

    >>> node_by_path(root, CustomPathIterator())
    <BaseNode object 'sub' at ...>


Debug helper
------------

.. code-block:: pycon

    >>> import logging
    >>> from node.utils import logger
    >>> from node.utils import debug

    >>> class TestHandler(logging.StreamHandler):
    ...     def handle(self, record):
    ...         print record
    >>> handler = TestHandler()
    >>> logger.addHandler(handler)
    >>> logger.setLevel(logging.DEBUG)

    >>> @debug
    ... def test_search(a, b=42):
    ...     pass

    >>> test_search(21)
    <LogRecord: node, 10, ...utils.py, ..., "test_search: args=(21,), kws={}">
    <LogRecord: node, 10, ...utils.py, ..., "test_search: --> None">

    >>> logger.setLevel(logging.INFO)
    >>> logger.removeHandler(handler)

"""