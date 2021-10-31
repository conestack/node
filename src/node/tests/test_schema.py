from node import schema
from node.base import BaseNode
from node.behaviors import Schema
from node.behaviors.schema import scope_field
from node.interfaces import ISchema
from node.tests import NodeTestCase
from node.utils import UNSET
from plumber import plumbing
import uuid


class TestSchema(NodeTestCase):

    def test_Field(self):
        field = schema.Field()

        self.assertEqual(field.default, UNSET)
        self.assertEqual(field.serialize('value'), 'value')
        self.assertEqual(field.deserialize('value'), 'value')

        self.assertEqual(field.type_, UNSET)
        self.assertTrue(field.validate('value'))

        field.type_ = int
        self.assertTrue(field.validate(1))
        self.assertFalse(field.validate('1'))

        parent = object()
        field.set_scope('name', parent)
        self.assertEqual(field.name, 'name')
        self.assertTrue(field.parent is parent)

        field.reset_scope()
        self.assertEqual(field.name, None)
        self.assertEqual(field.parent, None)

    def test_Int(self):
        field = schema.Int()
        self.assertTrue(field.validate(1))
        self.assertFalse(field.validate('1'))

    def test_Float(self):
        field = schema.Float()
        self.assertTrue(field.validate(1.))
        self.assertFalse(field.validate(1))

    def test_Bytes(self):
        field = schema.Bytes()
        self.assertTrue(field.validate(b'xxx'))
        self.assertFalse(field.validate(u'xxx'))

    def test_Str(self):
        field = schema.Str()
        self.assertTrue(field.validate(u'xxx'))
        self.assertFalse(field.validate(b'xxx'))

    def test_Tuple(self):
        field = schema.Tuple()
        self.assertTrue(field.validate((1, 2)))
        self.assertFalse(field.validate([1, 2]))

    def test_List(self):
        field = schema.List()
        self.assertTrue(field.validate([1, 2]))
        self.assertFalse(field.validate((1, 2)))

    def test_Dict(self):
        field = schema.Dict()
        self.assertTrue(field.validate({}))
        self.assertFalse(field.validate([]))

    def test_Set(self):
        field = schema.Set()
        self.assertTrue(field.validate({1, 2}))
        self.assertFalse(field.validate([]))

    def test_UUID(self):
        field = schema.UUID()
        self.assertTrue(field.validate(uuid.uuid4()))
        self.assertFalse(field.validate('1234'))

    def test_Node(self):
        field = schema.Node()
        self.assertTrue(field.validate(BaseNode()))
        self.assertFalse(field.validate(object()))

        parent = BaseNode()
        field.set_scope('name', parent)
        node = field.deserialize('some-non-node-data')
        self.assertIsInstance(node, BaseNode)
        self.assertEqual(node.name, 'name')
        self.assertTrue(node.parent is parent)

    def test_scope_field(self):
        field = schema.Field()
        parent = object()
        with scope_field(field, 'name', parent):
            self.assertEqual(field.name, 'name')
            self.assertTrue(field.parent is parent)
        self.assertEqual(field.name, None)
        self.assertEqual(field.parent, None)

    def test_Schema(self):
        @plumbing(Schema)
        class SchemaNode(BaseNode):
            allow_non_node_childs = True
            schema = {
                'int': schema.Int(),
                'float': schema.Float(default=1.),
                'str': schema.Str()
            }

        node = SchemaNode()
        self.assertTrue(ISchema.providedBy(node))

        node['any'] = 'foo'
        self.assertRaises(ValueError, node.__setitem__, 'int', '1')
        node['int'] = 0

        self.checkOutput("""
        <class 'node.tests.test_schema.SchemaNode'>: None
          any: 'foo'
          int: 0
        """, node.treerepr())

        self.assertEqual(node['any'], 'foo')
        self.assertEqual(node['int'], 0)
        self.assertEqual(node['float'], 1.)
        self.assertRaises(KeyError, node.__getitem__, 'str')

        node.schema['*'] = schema.UUID()
        self.assertRaises(ValueError, node.__setitem__, 'arbitrary', '1234')
        node['arbitrary'] = uuid.uuid4()
