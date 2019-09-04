from node.behaviors import DictStorage
from node.behaviors import OdictStorage
from node.behaviors import Storage
from node.tests import NodeTestCase
from odict import odict
from plumber import plumbing


###############################################################################
# Mock objects
###############################################################################

@plumbing(Storage)
class AbstractStorageObject(object):
    pass


@plumbing(DictStorage)
class DictStorageObject(object):
    pass


@plumbing(OdictStorage)
class OdictStorageObject(object):
    pass


###############################################################################
# Tests
###############################################################################

class TestStorage(NodeTestCase):

    def test_abstract_storage(self):
        obj = AbstractStorageObject()

        def access_storage_fails():
            obj.storage
        err = self.expectError(NotImplementedError, access_storage_fails)
        expected = 'Abstract storage does not implement ``storage``'
        self.assertEqual(str(err), expected)

    def test_dict_storage(self):
        obj = DictStorageObject()
        self.assertEqual(obj.storage, {})

        obj['foo'] = 'foo'
        self.assertEqual(obj.storage, {'foo': 'foo'})
        self.assertEqual(obj['foo'], 'foo')
        self.assertEqual([key for key in obj], ['foo'])

        del obj['foo']
        self.assertEqual(obj.storage, {})

    def test_odict_storage(self):
        obj = OdictStorageObject()
        self.assertEqual(obj.storage, odict())

        obj['foo'] = 'foo'
        self.assertEqual(obj.storage, odict([('foo', 'foo')]))
        self.assertEqual(obj['foo'], 'foo')
        self.assertEqual([key for key in obj], ['foo'])

        del obj['foo']
        self.assertEqual(obj.storage, odict())
