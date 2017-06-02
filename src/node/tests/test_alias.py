from node.behaviors import Alias
from node.behaviors.alias import AliaserChain
from node.behaviors.alias import DictAliaser
from node.behaviors.alias import PrefixAliaser
from node.behaviors.alias import PrefixSuffixAliaser
from node.behaviors.alias import SuffixAliaser
from node.tests import NodeTestCase
from plumber import plumbing


class TestAlias(NodeTestCase):

    def test_DictAliaser(self):
        # A dict aliaser takes a dictionary as base for aliasing
        da = DictAliaser([('alias1', 'key1'), ('alias2', 'key2')])
        self.assertEqual(da.alias('key1'), 'alias1')
        self.assertEqual(da.unalias('alias2'), 'key2')

        # By default, aliasing is strict, which means that only key/value pairs
        # set in aliaser are valid
        err = self.expect_error(KeyError, da.alias, 'foo')
        self.assertEqual(str(err), '\'foo\'')
        err = self.expect_error(KeyError, da.unalias, 'foo')
        self.assertEqual(str(err), '\'foo\'')

        # By setting strict to False, inexistent keys are returned as fallback
        da = DictAliaser(
            [('alias1', 'key1'), ('alias2', 'key2')],
            strict=False
        )
        self.assertEqual(da.alias('foo'), 'foo')
        self.assertEqual(da.unalias('foo'), 'foo')

    def test_PrefixAliaser(self):
        # An aliaser that simply prefixes all keys
        pa = PrefixAliaser('prefix-')
        self.assertEqual(pa.alias('foo'), 'prefix-foo')
        self.assertEqual(pa.unalias('prefix-foo'), 'foo')

        err = self.expect_error(KeyError, pa.unalias, 'foo')
        expected = '"key \'foo\' does not match prefix \'prefix-\'"'
        self.assertTrue(str(err).find(expected) > -1)

    def test_SuffixAliaser(self):
        # An aliaser that simply suffixes all keys
        sa = SuffixAliaser('-suffix')
        self.assertEqual(sa.alias('foo'), 'foo-suffix')
        self.assertEqual(sa.unalias('foo-suffix'), 'foo')

        err = self.expect_error(KeyError, sa.unalias, 'foo')
        expected = '"key \'foo\' does not match suffix \'-suffix\'"'
        self.assertTrue(str(err).find(expected) > -1)

    def test_AliaserChain(self):
        # A chain of aliasers
        aliaser = AliaserChain()

        pa = PrefixAliaser('prefix-')
        pa2 = PrefixAliaser('pre2-')

        aliaser.chain = [pa, pa2]
        self.assertEqual(aliaser.alias('foo'), 'pre2-prefix-foo')
        self.assertEqual(aliaser.unalias(aliaser.alias('foo')), 'foo')

        aliaser.chain = [pa2, pa]
        self.assertEqual(aliaser.unalias(aliaser.alias('foo')), 'foo')

    def test_PrefixSuffixAliaser(self):
        # Combined prefix and suffix aliaser
        psa = PrefixSuffixAliaser('prefix-', '-suffix')
        self.assertEqual(psa.alias('foo'), 'prefix-foo-suffix')
        self.assertEqual(psa.unalias(psa.alias('foo')), 'foo')

    def test_Alias_no_aliaser(self):
        # A dictionary that uses the alias plumbing but does not assign an
        # aliaser. Therefore, no aliasing is happening
        @plumbing(Alias)
        class AliasDict(dict):
            pass

        ad = AliasDict()
        ad['foo'] = 1
        self.assertEqual(ad['foo'], 1)
        self.assertEqual([x for x in ad], ['foo'])

        del ad['foo']
        self.assertEqual([x for x in ad], [])

    def test_Alias_with_PrefixAliaser(self):
        # A dictionary that uses the alias plumbing with a prefix aliaser
        @plumbing(Alias)
        class AliasDict(dict):
            aliaser = PrefixAliaser(prefix="pre-")

        ad = AliasDict()
        ad['pre-foo'] = 1
        self.assertEqual(ad['pre-foo'], 1)
        self.assertEqual([x for x in ad], ['pre-foo'])

        del ad['pre-foo']
        self.assertEqual([x for x in ad], [])

    def test_KeyError_with_aliased_key(self):
        # KeyErrors in the backend are caught and re-raised with the value of
        # the aliased key
        class FakeDict(object):
            def __delitem__(self, key):
                raise KeyError(key)

            def __getitem__(self, key):
                raise KeyError(key)

            def __iter__(self):
                yield 'foo'

            def __setitem__(self, key, val):
                raise KeyError(key)

        @plumbing(Alias)
        class FailDict(FakeDict):
            aliaser = PrefixAliaser(prefix="pre-")

        fail = FailDict()

        def fail___setitem__():
            fail['pre-foo'] = 1
        err = self.expect_error(KeyError, fail___setitem__)
        self.assertEqual(str(err), '\'pre-foo\'')

        def fail___getitem__():
            fail['pre-foo']
        err = self.expect_error(KeyError, fail___getitem__)
        self.assertEqual(str(err), '\'pre-foo\'')

        def fail___delitem__():
            del fail['pre-foo']
        err = self.expect_error(KeyError, fail___delitem__)
        self.assertEqual(str(err), '\'pre-foo\'')

        # A prefix aliaser cannot raise a KeyError, nevertheless, if it does,
        # that error must not be caught by the code that handle alias KeyErrors
        # for whitelisting.

        def failalias(key):
            raise KeyError()

        fail.aliaser.alias = failalias

        def fail_alias():
            [x for x in fail]
        self.assertRaises(KeyError, fail_alias)

    def test_Alias_with_DictAliaser(self):
        # A dictionary that uses the alias plumbing with a dict aliaser
        @plumbing(Alias)
        class AliasDict(dict):
            aliaser = DictAliaser(data=(('foo', 'f00'), ('bar', 'b4r')))

        ad = AliasDict()
        ad['foo'] = 1
        self.assertEqual([x for x in ad], ['foo'])

        # Let's put a key in the dict, that is not mapped by the dictionary
        # aliaser. This is not possible through the plumbing ``__setitem__``,
        # we need to use ``dict.__setitem__``
        def fail___setitem__():
            ad['abc'] = 1
        err = self.expect_error(KeyError, fail___setitem__)
        self.assertEqual(str(err), '\'abc\'')

        dict.__setitem__(ad, 'abc', 1)
        self.assertEqual([x for x in ad], ['foo'])

        # To see the keys that are really in the dictionary, we use
        # ``dict.__iter__``, not the plumbing ``__iter__``
        self.assertEqual(
            [x for x in sorted(dict.__iter__(ad))],
            ['abc', 'f00']
        )
