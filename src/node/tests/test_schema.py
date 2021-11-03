from node import schema
from node.base import BaseNode
from node.behaviors import Schema
from node.behaviors import SchemaAsAttributes
from node.behaviors import SchemaAttributes
from node.behaviors.schema import scope_field
from node.interfaces import IAttributes
from node.interfaces import INodeAttributes
from node.interfaces import ISchema
from node.interfaces import ISchemaAsAttributes
from node.tests import NodeTestCase
from node.utils import AttributeAccess
from node.utils import UNSET
from plumber import plumbing
import uuid


class TestSchema(NodeTestCase):

    def test_Field(self):
        field = schema.Field()

        self.assertEqual(field.default, schema._undefined)
        self.assertEqual(field.serialize('value'), 'value')
        self.assertEqual(field.deserialize('value'), 'value')

        self.assertEqual(field.type_, schema._undefined)
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

    def test_Bool(self):
        field = schema.Bool()
        self.assertTrue(field.validate(True))
        self.assertFalse(field.validate(1))

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
            allow_non_node_children = True
            schema = {
                'int': schema.Int(),
                'float': schema.Float(default=1.),
                'str': schema.Str(),
                'bool': schema.Bool(default=UNSET)
            }

        node = SchemaNode()
        self.assertTrue(ISchema.providedBy(node))

        node['any'] = 'foo'
        with self.assertRaises(ValueError):
            node['int'] = '1'
        node['int'] = 0

        self.checkOutput("""
        <class 'node.tests.test_schema.SchemaNode'>: None
        __any: 'foo'
        __int: 0
        """, node.treerepr(prefix='_'))

        self.assertEqual(node['any'], 'foo')
        self.assertEqual(node['int'], 0)
        self.assertEqual(node['float'], 1.)
        self.assertEqual(node['bool'], UNSET)
        with self.assertRaises(KeyError):
            node['str']

        node.schema['*'] = schema.UUID()
        with self.assertRaises(ValueError):
            node['arbitrary'] = '1234'
        node['arbitrary'] = uuid.uuid4()

    def test_SchemaAsAttributes(self):
        @plumbing(SchemaAsAttributes)
        class SchemaAsAttributesNode(BaseNode):
            schema = {
                'int': schema.Int(),
                'float': schema.Float(default=1.),
                'str': schema.Str(),
                'bool': schema.Bool()
            }

        node = SchemaAsAttributesNode()
        self.assertTrue(IAttributes.providedBy(node))
        self.assertTrue(ISchemaAsAttributes.providedBy(node))

        attrs = node.attrs
        self.assertTrue(INodeAttributes.providedBy(attrs))
        self.assertIsInstance(attrs, SchemaAttributes)
        self.assertEqual(sorted(iter(attrs)), ['bool', 'float', 'int', 'str'])

        attrs['int'] = 1
        attrs['float'] = 2.
        attrs['str'] = u'foo'
        attrs['bool'] = True
        self.assertEqual(node.storage, {
            'float': 2.,
            'int': 1,
            'str': u'foo',
            'bool': True
        })
        del attrs['bool']
        with self.assertRaises(ValueError):
            attrs['str'] = 1
        with self.assertRaises(KeyError):
            attrs['other']
        with self.assertRaises(KeyError):
            attrs['other'] = 'value'
        with self.assertRaises(KeyError):
            del attrs['other']

        node.attribute_access_for_attrs = True
        attrs = node.attrs
        self.assertIsInstance(attrs, AttributeAccess)
        self.assertEqual(attrs.int, 1)
        self.assertEqual(attrs.float, 2.)
        self.assertEqual(attrs.str, u'foo')

        attrs.int = 2
        attrs.float = 3.
        attrs.str = u'bar'
        self.assertEqual(node.storage, {'float': 3., 'int': 2, 'str': u'bar'})

        child = node['child'] = BaseNode()
        self.checkOutput("""
        <class 'node.tests.test_schema.SchemaAsAttributesNode'>: None
        __<class 'node.base.BaseNode'>: child
        """, node.treerepr(prefix='_'))

        self.assertEqual(list(iter(node)), ['child'])
        self.assertTrue(node['child'] is child)
        del node['child']

        self.checkOutput("""
        <class 'node.tests.test_schema.SchemaAsAttributesNode'>: None
        """, node.treerepr(prefix='_'))

        with self.assertRaises(KeyError):
            node['int'] = 1
        with self.assertRaises(KeyError):
            node['int']
        with self.assertRaises(KeyError):
            del node['int']
