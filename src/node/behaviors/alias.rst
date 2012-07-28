node.behaviors.alias
====================


DictAliaser
-----------

A dict aliaser takes a dictionary as base for aliasing::

    >>> from node.behaviors.alias import DictAliaser
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

    >>> from node.behaviors.alias import PrefixAliaser
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

    >>> from node.behaviors.alias import SuffixAliaser
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

    >>> from node.behaviors.alias import AliaserChain
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

    >>> from node.behaviors.alias import PrefixSuffixAliaser
    >>> psa = PrefixSuffixAliaser('prefix-', '-suffix')
    >>> psa.alias('foo')
    'prefix-foo-suffix'
    
    >>> psa.unalias(psa.alias('foo'))
    'foo'


Alias
-----

A dictionary that uses the alias plumbing but does not assign an aliaser.
Therefore, no aliasing is happening::

    >>> from plumber import plumber
    >>> from node.behaviors import Alias
    >>> class AliasDict(dict):
    ...     __metaclass__ = plumber
    ...     __plumbing__ = Alias

    >>> ad = AliasDict()
    >>> ad['foo'] = 1
    >>> ad['foo']
    1
    
    >>> [x for x in ad]
    ['foo']
    
    >>> del ad['foo']
    >>> [x for x in ad]
    []

Now the same but with a prefix aliaser::

    >>> from node.behaviors.alias import PrefixAliaser
    >>> aliaser = PrefixAliaser(prefix="pre-")
    >>> ad = AliasDict()
    >>> ad.aliaser = aliaser
    >>> ad['pre-foo'] = 1
    >>> ad['pre-foo']
    1
    
    >>> [x for x in ad]
    ['pre-foo']
    
    >>> del ad['pre-foo']
    >>> [x for x in ad]
    []

KeyErrors in the backend are caught and re-raised with the value of the aliased
key::

    >>> class FakeDict(object):
    ...     def __delitem__(self, key):
    ...         raise KeyError(key)
    ...     def __getitem__(self, key):
    ...         raise KeyError(key)
    ...     def __iter__(self):
    ...         yield 'foo'
    ...     def __setitem__(self, key, val):
    ...         raise KeyError(key)

    >>> class FailDict(FakeDict):
    ...     __metaclass__ = plumber
    ...     __plumbing__ = Alias

    >>> fail = FailDict()
    >>> fail.aliaser = aliaser
    >>> fail['pre-foo'] = 1
    Traceback (most recent call last):
    ...
    KeyError: 'pre-foo'

    >>> fail['pre-foo']
    Traceback (most recent call last):
    ...
    KeyError: 'pre-foo'

    >>> del fail['pre-foo']
    Traceback (most recent call last):
    ...
    KeyError: 'pre-foo'

A prefix aliaser cannot raise a KeyError, nevertheless, if it does, that error
must not be caught by the code that handle alias KeyErrors for whitelisting
(see below)::

    >>> def failalias(key):
    ...     raise KeyError
    
    >>> fail.aliaser.alias = failalias
    >>> [x for x in fail]
    Traceback (most recent call last):
    ...
    KeyError

    >>> from node.behaviors.alias import DictAliaser
    >>> dictaliaser = DictAliaser(data=(('foo', 'f00'), ('bar', 'b4r')))

    >>> ad = AliasDict()
    >>> ad.aliaser = dictaliaser
    >>> ad['foo'] = 1
    >>> [x for x in ad]
    ['foo']

Let's put a key in the dict, that is not mapped by the dictionary aliaser. This
is not possible through the plumbing ``__setitem__``, we need to use
``dict.__setitem``::

    >>> ad['abc'] = 1
    Traceback (most recent call last):
    ...
    KeyError: 'abc'

    >>> dict.__setitem__(ad, 'abc', 1)
    >>> [x for x in ad]
    ['foo']

To see the keys that are really in the dictionary, we use ``dict.__iter__``,
not the plumbing ``__iter__``::

    >>> [x for x in dict.__iter__(ad)]
    ['abc', 'f00']
