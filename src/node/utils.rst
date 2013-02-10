# -*- coding: utf-8 -*-

node.utils
==========


UNSET
-----

::
    >>> from node.utils import UNSET
    >>> UNSET
    <UNSET>

    >>> str(UNSET)
    ''

    >>> bool(UNSET)
    False

    >>> len(UNSET)
    0


ReverseMapping
--------------

::
    >>> from node.utils import ReverseMapping
    >>> context = {
    ...     'foo': 'a',
    ...     'bar': 'b',
    ... }
    >>> mapping = ReverseMapping(context)

    >>> [v for v in mapping]
    ['a', 'b']

    >>> mapping.keys()
    ['a', 'b']
    
    >>> mapping.values()
    ['foo', 'bar']
    
    >>> mapping.items()
    [('a', 'foo'), ('b', 'bar')]
    
    >>> len(mapping)
    2
    
    >>> 'a' in mapping
    True
    
    >>> 'foo' in mapping
    False
    
    >>> mapping['a']
    'foo'
    
    >>> mapping['foo']
    Traceback (most recent call last):
      ...
    KeyError: 'foo'
    
    >>> mapping.get('b')
    'bar'
    
    >>> mapping.get('foo', 'DEFAULT')
    'DEFAULT'


AttributeAccess
---------------

::
    >>> from node.utils import AttributeAccess
    >>> attraccess = AttributeAccess(context)
    >>> attraccess.foo
    'a'
    
    >>> attraccess.a
    Traceback (most recent call last):
      ...
    AttributeError: a
    
    >>> attraccess.foo = 'foo'
    >>> attraccess.foo
    'foo'
    
    >>> attraccess['foo']
    'foo'
    
    >>> attraccess['baz'] = 'bla'
    >>> attraccess.baz
    'bla'
    
    >>> del attraccess['bar']
    >>> object.__getattribute__(attraccess, 'context').keys()
    ['baz', 'foo']

    >>> attraccess.x = 0
    >>> object.__getattribute__(attraccess, 'context').keys()
    ['baz', 'foo', 'x']


StrCodec decode and encode
--------------------------

::
    >>> from node.base import BaseNode
    >>> from node.utils import (
    ...     StrCodec,
    ...     encode,
    ...     decode,
    ... )
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


Debug helper
------------

::
    >>> import logging
    >>> from node.utils import (
    ...     logger,
    ...     debug,
    ... )
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
