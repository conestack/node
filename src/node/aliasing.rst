node.aliasing
=============

DictAliaser
-----------

A dict aliaser takes a dictionary as base for aliasing::

    >>> from node.aliasing import DictAliaser
    >>> da = DictAliaser([('alias1', 'key1'), ('alias2', 'key2')])

    >>> da.alias('key1')
    'alias1'

    >>> da.unalias('alias2')
    'key2'

By default, aliasing is strict, which means that only key/value pairs set in
aliaser are valid::

    >>> da.alias('foo')
    Traceback (most recent call last):
    ...
    KeyError: 'foo'

    >>> da.unalias('foo')
    Traceback (most recent call last):
    ...
    KeyError: 'foo'

By setting strict to False, inexistent keys are returned as fallback::

    >>> da = DictAliaser([('alias1', 'key1'), ('alias2', 'key2')], strict=False)
    >>> da.alias('foo')
    'foo'
    
    >>> da.unalias('foo')
    'foo'


PrefixAliaser
-------------

An aliaser that simply prefixes all keys.::

    >>> from node.aliasing import PrefixAliaser
    >>> pa = PrefixAliaser('prefix-')
    
    >>> pa.alias('foo')
    'prefix-foo'

    >>> pa.unalias('prefix-foo')
    'foo'

    >>> pa.unalias('foo')
    Traceback (most recent call last):
    ...
    KeyError: u"key 'foo' does not match prefix 'prefix-'"


SuffixAliaser
-------------

An aliaser that simply suffixes all keys.::

    >>> from node.aliasing import SuffixAliaser
    >>> sa = SuffixAliaser('-suffix')
    
    >>> sa.alias('foo')
    'foo-suffix'

    >>> sa.unalias('foo-suffix')
    'foo'

    >>> sa.unalias('foo')
    Traceback (most recent call last):
    ...
    KeyError: u"key 'foo' does not match suffix '-suffix'"


AliaserChain
------------

A chain of aliasers.::

    >>> from node.aliasing import AliaserChain
    >>> aliaser = AliaserChain()
    >>> pa2 = PrefixAliaser('pre2-')
    >>> aliaser.chain = [pa, pa2]
    >>> aliaser.alias('foo')
    'pre2-prefix-foo'

    >>> aliaser.unalias(aliaser.alias('foo'))
    'foo'

    >>> aliaser.chain = [pa2, pa]
    >>> aliaser.unalias(aliaser.alias('foo'))
    'foo'


PrefixSuffixAliaser
-------------------

Combined prefix and suffix aliaser::

    >>> from node.aliasing import PrefixSuffixAliaser
    >>> psa = PrefixSuffixAliaser('prefix-', '-suffix')
    >>> psa.alias('foo')
    'prefix-foo-suffix'
    
    >>> psa.unalias(psa.alias('foo'))
    'foo'


AliasedNodespace
----------------

Set aliases for a Nodespace, i.e. attributes Nodespace::

    >>> from node.aliasing import AliasedNodespace
    >>> from node.base import AttributedNode
    >>> node = AttributedNode()
    >>> attrs = node.attrs
    >>> aliaser = DictAliaser([('alias1', 'key1'), ('alias2', 'key2')])
    >>> aliased_ns = AliasedNodespace(attrs, aliaser)
    >>> aliased_ns.allow_non_node_childs = True
    >>> aliased_ns
    Aliased <NodeAttributes object 'None' at ...>

__setitem__::

    >>> aliased_ns['alias1'] = 'foo'

Strict mode does not allow setting of non available aliases::

    >>> aliased_ns['foo'] = 'foo'
    Traceback (most recent call last):
      ...
    KeyError: 'foo'

__getitem__::

    >>> aliased_ns['alias1']
    'foo'
    
    >>> aliased_ns.context['key1']
    'foo'

__iter__::

    >>> aliased_ns.keys()
    ['alias1']

Second aliased item not set yet::

    >>> aliased_ns['alias2']
    Traceback (most recent call last):
      ...
    KeyError: 'alias2'
    
    >>> aliased_ns['alias2'] = 'foo'
    >>> aliased_ns.keys()
    ['alias1', 'alias2']

Also non available aliased items are not available if dict aliaser in strict
mode::

    >>> aliased_ns.context['key3'] = 'baz'
    >>> aliased_ns.keys()
    ['alias1', 'alias2']

__delitem__::

    >>> del aliased_ns['alias2']
    >>> aliased_ns.keys()
    ['alias1']
    
    >>> del aliased_ns['alias2']
    Traceback (most recent call last):
      ...
    KeyError: 'alias2'
    
In strict mode you cannot delete unaliased items::

    >>> del aliased_ns['key3']
    Traceback (most recent call last):
      ...
    KeyError: 'key3'

Test non strict::

    >>> aliaser = DictAliaser([('alias1', 'key1'),], strict=False)
    >>> aliased_ns.aliaser = aliaser

__setitem__::

    >>> aliased_ns['alias1'] = 'bar'
    >>> aliased_ns['foo'] = 'bar'

__getitem__::

    >>> aliased_ns['foo']
    'bar'
    
    >>> aliased_ns.context['foo']
    'bar'
    
    >>> aliased_ns['alias1']
    'bar'
    
    >>> aliased_ns.context['key1']
    'bar'
    
    >>> aliased_ns['inexistent']
    Traceback (most recent call last):
      ...
    KeyError: 'inexistent'

__iter__::

    >>> aliased_ns.keys()
    ['alias1', 'key3', 'foo']
    
    >>> aliased_ns.context.keys()
    ['key1', 'key3', 'foo']

__delitem__::

    >>> del aliased_ns['alias1']
    >>> aliased_ns.keys()
    ['key3', 'foo']
    
    >>> del aliased_ns['alias1']
    Traceback (most recent call last):
      ...
    KeyError: 'alias1'

    >>> del aliased_ns['foo']
    >>> aliased_ns.keys()
    ['key3']
    
    >>> del aliased_ns['foo']
    Traceback (most recent call last):
      ...
    KeyError: 'foo'
