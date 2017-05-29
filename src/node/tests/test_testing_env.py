from node.testing.env import MyNode
import sys


if sys.version_info < (2, 7):                                # pragma: no cover
    import unittest2 as unittest
else:                                                        # pragma: no cover
    import unittest


class TestEnv(unittest.TestCase):

    def test_fullmapping(self):
        mynode = MyNode()
        self.assertIsInstance(mynode, MyNode)
        # __setitem__
        foo = mynode['foo'] = MyNode()
        bar = mynode['bar'] = MyNode(name='xxx')
        # __getitem__
        self.assertEqual(mynode['foo'], foo)
        self.assertEqual(mynode['bar'].__name__, 'bar')
        # get
        self.assertEqual(mynode.get('bar'), bar)
        self.assertEqual(mynode.get('xxx', 'default'), 'default')
        # __iter__
        self.assertEqual([key for key in mynode], ['foo', 'bar'])
        # keys
        self.assertEqual(mynode.keys(), ['foo', 'bar'])
        # iterkeys
        self.assertEqual([key for key in mynode.iterkeys()], ['foo', 'bar'])
        # values
        self.assertEqual(mynode.values(), [foo, bar])
        # itervalues
        self.assertEqual([val for val in mynode.itervalues()], [foo, bar])
        # items
        self.assertEqual(mynode.items(), [
            ('foo', foo),
            ('bar', bar)
        ])
        # iteritems
        self.assertEqual([item for item in mynode.iteritems()], [
            ('foo', foo),
            ('bar', bar)
        ])
        # __contains__
        self.assertTrue('bar' in mynode)
        # has_key
        self.assertTrue(mynode.has_key('foo'))
        # __len__
        self.assertEqual(len(mynode), 2)
        # update
        baz = MyNode()
        mynode.update((('baz', baz),))
        self.assertEqual(mynode['baz'], baz)
        # __delitem__
        del mynode['bar']
        self.assertEqual(mynode.keys(), ['foo', 'baz'])
        # copy
        mycopied = mynode.copy()
        self.assertTrue(str(mycopied).find('<MyNode object \'None\' at ') > -1)
        self.assertFalse(mycopied is mynode)
        self.assertTrue(mycopied['foo'] is foo)
        self.assertTrue(mycopied['baz'] is baz)
        self.assertEqual(mycopied.items(), [
            ('foo', foo),
            ('baz', baz)
        ])
        # setdefault
        mynew = MyNode()
        self.assertFalse(mynode.setdefault('foo', mynew) is mynew)
        self.assertTrue(mynode.setdefault('bar', mynew) is mynew)
        self.assertEqual(mynode.items(), [
            ('foo', foo),
            ('baz', baz),
            ('bar', mynew)
        ])
        # pop
        self.assertRaises(KeyError, mynode.pop, 'xxx')
        self.assertEqual(mynode.pop('xxx', 'default'), 'default')
        self.assertEqual(mynode.pop('foo'), foo)
        self.assertEqual(mynode.keys(), ['baz', 'bar'])
        # popitem and clear
        self.assertEqual(mynode.popitem(), ('bar', mynew))
        self.assertEqual(mynode.keys(), ['baz'])
        mynode.clear()
        self.assertEqual(mynode.keys(), [])
        self.assertRaises(KeyError, mynode.popitem)


if __name__ == '__main__':
    unittest.main()                                          # pragma: no cover
