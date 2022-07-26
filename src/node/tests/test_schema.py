from node import compat
from node import schema
from node.base import BaseNode
from node.behaviors import Schema
from node.behaviors import SchemaAsAttributes
from node.behaviors import SchemaAttributes
from node.behaviors import SchemaProperties
from node.interfaces import IAttributes
from node.interfaces import INodeAttributes
from node.interfaces import ISchema
from node.interfaces import ISchemaAsAttributes
from node.tests import NodeTestCase
from node.utils import AttributeAccess
from node.utils import UNSET
from odict import odict
from plumber import plumbing
import datetime
import unittest
import uuid


class TestObject(object):

    def __init__(self, value):
        self.value = value


class TestSchemaScope(unittest.TestCase):

    def test_scope_context(self):
        context = schema.ScopeContext()
        parent = object()
        with schema.scope_context(context, 'name', parent):
            self.assertEqual(context.name, 'name')
            self.assertTrue(context.parent is parent)
        self.assertEqual(context.name, None)
        self.assertEqual(context.parent, None)


class TestSchemaSerializer(unittest.TestCase):

    def test_FieldSerializer(self):
        serializer = schema.FieldSerializer()
        with self.assertRaises(NotImplementedError):
            serializer.dump(None)
        with self.assertRaises(NotImplementedError):
            serializer.load(None)

        self.assertIsInstance(serializer, schema.ScopeContext)
        parent = object()
        with schema.scope_context(serializer, 'name', parent):
            self.assertEqual(serializer.name, 'name')
            self.assertEqual(serializer.parent, parent)
        self.assertEqual(serializer.name, None)
        self.assertEqual(serializer.parent, None)

    def test_TypeSerializer(self):
        serializer = schema.TypeSerializer(int)
        self.assertIsInstance(serializer, schema.FieldSerializer)
        self.assertEqual(serializer.type_, int)
        self.assertEqual(serializer.dump(1), u'1')
        self.assertEqual(serializer.load(u'1'), 1)

    def test_int_serializer(self):
        serializer = schema.int_serializer
        self.assertIsInstance(serializer, schema.TypeSerializer)
        self.assertEqual(serializer.type_, int)
        self.assertEqual(serializer.dump(1), u'1')
        self.assertEqual(serializer.load(u'1'), 1)

    def test_float_serializer(self):
        serializer = schema.float_serializer
        self.assertIsInstance(serializer, schema.TypeSerializer)
        self.assertEqual(serializer.type_, float)
        self.assertEqual(serializer.dump(1.), u'1.0')
        self.assertEqual(serializer.load(u'1.0'), 1.)

    def test_uuid_serializer(self):
        serializer = schema.uuid_serializer
        self.assertIsInstance(serializer, schema.TypeSerializer)
        self.assertEqual(serializer.type_, uuid.UUID)
        uid = uuid.uuid4()
        self.assertEqual(serializer.dump(uid), str(uid))
        self.assertEqual(serializer.load(str(uid)), uid)

    def test_IterableSerializer(self):
        serializer = schema.IterableSerializer(list)
        self.assertIsInstance(serializer, schema.FieldSerializer)
        self.assertEqual(serializer.type_, list)
        self.assertEqual(serializer.dump([u'a', u'b', u'c']), u'a,b,c')
        self.assertEqual(serializer.load(u'a,b,c'), [u'a', u'b', u'c'])
        self.assertEqual(serializer.dump([u'a,', u'b', u'c']), u'a%2C,b,c')
        self.assertEqual(serializer.load(u'a%2C,b,c'), [u'a,', u'b', u'c'])

    def test_list_serializer(self):
        serializer = schema.list_serializer
        self.assertIsInstance(serializer, schema.IterableSerializer)
        self.assertEqual(serializer.type_, list)
        self.assertEqual(serializer.dump([u'a', u'b', u'c']), u'a,b,c')
        self.assertEqual(serializer.load(u'a,b,c'), [u'a', u'b', u'c'])

    def test_tuple_serializer(self):
        serializer = schema.tuple_serializer
        self.assertIsInstance(serializer, schema.IterableSerializer)
        self.assertEqual(serializer.type_, tuple)
        self.assertEqual(serializer.dump((u'a', u'b', u'c')), u'a,b,c')
        self.assertEqual(serializer.load(u'a,b,c'), (u'a', u'b', u'c'))

    def test_set_serializer(self):
        serializer = schema.set_serializer
        self.assertIsInstance(serializer, schema.IterableSerializer)
        self.assertEqual(serializer.type_, set)
        self.assertEqual(serializer.dump({u'a', u'b', u'c'}), u'a,b,c')
        self.assertEqual(serializer.load(u'a,b,c'), {u'a', u'b', u'c'})

    def test_MappingSerializer(self):
        serializer = schema.MappingSerializer(dict)
        self.assertIsInstance(serializer, schema.FieldSerializer)
        self.assertEqual(serializer.type_, dict)
        self.assertEqual(serializer.dump({u'foo,': u'bar;'}), u'foo%2C,bar%3B')
        self.assertEqual(serializer.load(u'foo%2C,bar%3B'), {u'foo,': u'bar;'})

    def test_dict_serializer(self):
        serializer = schema.dict_serializer
        self.assertIsInstance(serializer, schema.MappingSerializer)
        self.assertEqual(serializer.type_, dict)
        self.assertEqual(serializer.dump({u'foo': u'bar'}), u'foo,bar')
        self.assertEqual(serializer.load(u'foo,bar'), {u'foo': u'bar'})

    def test_odict_serializer(self):
        serializer = schema.odict_serializer
        self.assertIsInstance(serializer, schema.MappingSerializer)
        self.assertEqual(serializer.type_, odict)
        od = odict()
        od[u'foo'] = u'bar,'
        od[u'baz'] = u'bam'
        self.assertEqual(serializer.dump(od), u'foo,bar%2C;baz,bam')
        self.assertEqual(serializer.load(u'foo,bar%2C;baz,bam'), od)

    def test_Base64Serializer(self):
        serializer = schema.Base64Serializer()
        self.assertIsInstance(serializer, schema.FieldSerializer)
        self.assertIsInstance(schema.base64_serializer, schema.Base64Serializer)
        self.assertEqual(serializer.dump(u'value'), u'dmFsdWU=')
        self.assertEqual(serializer.load(u'dmFsdWU='), u'value')

    def test_JSONSerializer(self):
        serializer = schema.JSONSerializer()
        self.assertIsInstance(serializer, schema.FieldSerializer)
        self.assertIsInstance(schema.json_serializer, schema.JSONSerializer)
        self.assertEqual(serializer.dump({u'foo': u'bar'}), u'{"foo": "bar"}')
        self.assertEqual(serializer.load(u'{"foo": "bar"}'), {u'foo': u'bar'})

    def test_PickleSerializer(self):
        serializer = schema.PickleSerializer()
        self.assertIsInstance(serializer, schema.FieldSerializer)
        self.assertIsInstance(schema.pickle_serializer, schema.PickleSerializer)
        data = serializer.dump(TestObject('value'))
        obj = serializer.load(data)
        self.assertIsInstance(obj, TestObject)
        self.assertEqual(obj.value, 'value')

    def test_DateTimeSerializer(self):
        serializer = schema.DateTimeSerializer()
        self.assertIsInstance(serializer, schema.FieldSerializer)
        self.assertIsInstance(schema.datetime_serializer, schema.DateTimeSerializer)
        self.assertEqual(
            serializer.dump(datetime.datetime(2022, 1, 1, 0, 0)),
            '2022-01-01T00:00:00.000000'
        )
        self.assertEqual(
            serializer.load('2022-01-01T00:00:00.000000'),
            datetime.datetime(2022, 1, 1, 0, 0)
        )

    def test_NodeSerializer(self):
        serializer = schema.NodeSerializer(BaseNode)
        self.assertIsInstance(serializer, schema.FieldSerializer)
        self.assertEqual(serializer.type_, BaseNode)
        node = BaseNode()
        self.assertEqual(serializer.dump(node), node)
        self.assertEqual(serializer.load(node), node)
        with schema.scope_context(serializer, 'name', node):
            self.assertEqual(serializer.load('data'), node['name'])


class TestSchemaFields(unittest.TestCase):

    def test_Field(self):
        field = schema.Field(str)
        self.assertEqual(field.type_, str)
        self.assertEqual(field.default, UNSET)
        self.assertEqual(field.serializer, UNSET)

        self.assertIsNone(field.validate('value'))
        with self.assertRaises(ValueError):
            field.validate(1)

        self.assertEqual(field.serialize('value'), 'value')
        self.assertEqual(field.deserialize('value'), 'value')

        field = schema.Field(uuid.UUID, serializer=schema.uuid_serializer)
        self.assertEqual(field.type_, uuid.UUID)
        self.assertEqual(field.serializer, schema.uuid_serializer)
        uid = uuid.uuid4()
        self.assertIsNone(field.validate(uid))
        with self.assertRaises(ValueError):
            field.validate(1)

        self.assertEqual(field.serialize(uid), str(uid))
        self.assertEqual(field.deserialize(str(uid)), uid)

        self.assertIsInstance(field, schema.ScopeContext)
        parent = object()
        with schema.scope_context(field, 'name', parent):
            self.assertEqual(field.name, 'name')
            self.assertEqual(field.parent, parent)
        self.assertEqual(field.name, None)
        self.assertEqual(field.parent, None)

        class TestSerializer(schema.FieldSerializer):
            def dump(self, value):
                return self.name, self.parent

            def load(self, value):
                return self.name, self.parent

        serializer = TestSerializer()
        field = schema.Field(str, serializer=serializer)
        self.assertEqual(field.serializer, serializer)
        with schema.scope_context(field, 'name', parent):
            self.assertEqual(field.serialize(None), ('name', parent))
            self.assertEqual(field.deserialize(None), ('name', parent))
        self.assertEqual(field.serialize(None), (None, None))
        self.assertEqual(field.deserialize(None), (None, None))

    def test_IterableField(self):
        field = schema.IterableField(list)
        self.assertIsInstance(field, schema.Field)
        self.assertEqual(field.type_, list)
        self.assertEqual(field.serializer, UNSET)
        self.assertEqual(field.default, UNSET)
        self.assertEqual(field.value_type, UNSET)
        self.assertEqual(field.size, UNSET)

        self.assertIsNone(field.validate([]))
        with self.assertRaises(ValueError):
            field.validate(set())
        self.assertEqual(field.serialize([]), [])
        self.assertEqual(field.deserialize([]), [])

        field = schema.IterableField(list, size=1)
        self.assertIsNone(field.validate([1]))
        with self.assertRaises(ValueError):
            field.validate([])

        field = schema.IterableField(list, value_type=schema.Int())
        self.assertIsNone(field.validate([1]))
        with self.assertRaises(ValueError):
            field.validate(['1'])

        field = schema.IterableField(tuple, serializer=schema.list_serializer)
        self.assertEqual(field.serialize((u'a', u'b', u'c')), u'a,b,c')
        self.assertEqual(field.deserialize(u'a,b,c'), (u'a', u'b', u'c'))
        with self.assertRaises(AttributeError if compat.IS_PY2 else TypeError):
            field.serialize([1, 2, 3])

        field = schema.IterableField(
            tuple,
            serializer=schema.tuple_serializer,
            value_type=schema.Int(serializer=schema.int_serializer)
        )
        self.assertEqual(field.serialize((1, 2, 3)), u'1,2,3')
        self.assertEqual(field.deserialize(u'1,2,3'), (1, 2, 3))

        field = schema.IterableField(
            set,
            serializer=schema.set_serializer,
            value_type=schema.UUID(serializer=schema.uuid_serializer)
        )
        uid = uuid.UUID(u'1f4be432-a693-44bd-9eb8-e0b8d3aec82d')
        self.assertEqual(
            field.serialize({uid}),
            u'1f4be432-a693-44bd-9eb8-e0b8d3aec82d'
        )
        self.assertEqual(
            field.deserialize(u'1f4be432-a693-44bd-9eb8-e0b8d3aec82d'),
            {uid}
        )

    def test_nested_IterableField(self):
        field = schema.IterableField(list, value_type=schema.List(size=1))
        self.assertIsNone(field.validate([[1]]))
        with self.assertRaises(ValueError):
            field.validate([[1, 2]])

        field = schema.IterableField(
            list,
            serializer=schema.list_serializer,
            value_type=schema.Tuple(
                serializer=schema.tuple_serializer,
                value_type=schema.Int(serializer=schema.int_serializer)
            )
        )
        self.assertIsNone(field.validate([(1, 2), (3,)]))
        with self.assertRaises(ValueError):
            field.validate([(1, 2), 3])
        self.assertEqual(field.serialize([(1, 2), (3,)]), u'1%2C2,3')
        self.assertEqual(field.deserialize(u'1%2C2,3'), [(1, 2), (3,)])

        field = schema.IterableField(
            list,
            serializer=schema.list_serializer,
            value_type=schema.Set(
                serializer=schema.set_serializer,
                value_type=schema.Tuple(
                    serializer=schema.tuple_serializer,
                    value_type=schema.Int(serializer=schema.int_serializer)
                )
            )
        )
        self.assertIsNone(field.validate([{(1, 2)}, {(3,)}]))
        with self.assertRaises(ValueError):
            field.validate([{(1, 2)}, {3}])
        self.assertEqual(field.serialize([{(1, 2)}, {(3,)}]), u'1%252C2,3')
        self.assertEqual(field.deserialize(u'1%252C2,3'), [{(1, 2)}, {(3,)}])

    def test_Bool(self):
        field = schema.Bool()
        self.assertIsInstance(field, schema.Field)
        self.assertIsNone(field.validate(True))
        with self.assertRaises(ValueError):
            field.validate(1)

    def test_Int(self):
        field = schema.Int()
        self.assertIsInstance(field, schema.Field)
        self.assertIsNone(field.validate(1))
        with self.assertRaises(ValueError):
            field.validate('1')

    def test_Float(self):
        field = schema.Float()
        self.assertIsInstance(field, schema.Field)
        self.assertIsNone(field.validate(1.))
        with self.assertRaises(ValueError):
            field.validate(1)

    def test_Bytes(self):
        field = schema.Bytes()
        self.assertIsInstance(field, schema.Field)
        self.assertIsNone(field.validate(b'xxx'))
        with self.assertRaises(ValueError):
            field.validate(u'xxx')

    def test_Str(self):
        field = schema.Str()
        self.assertIsInstance(field, schema.Field)
        self.assertIsNone(field.validate(u'xxx'))
        with self.assertRaises(ValueError):
            field.validate(b'xxx')

    def test_UUID(self):
        field = schema.UUID()
        self.assertIsInstance(field, schema.Field)
        self.assertIsNone(field.validate(uuid.uuid4()))
        with self.assertRaises(ValueError):
            field.validate(u'1234')

    def test_DateTime(self):
        field = schema.DateTime()
        self.assertIsInstance(field, schema.Field)
        self.assertIsNone(field.validate(datetime.datetime.now()))
        with self.assertRaises(ValueError):
            field.validate(1)

    def test_Tuple(self):
        field = schema.Tuple()
        self.assertIsInstance(field, schema.IterableField)
        self.assertIsNone(field.validate((1, 2)))
        with self.assertRaises(ValueError):
            field.validate([1, 2])

    def test_List(self):
        field = schema.List()
        self.assertIsInstance(field, schema.IterableField)
        self.assertIsNone(field.validate([1, 2]))
        with self.assertRaises(ValueError):
            field.validate((1, 2))

    def test_Set(self):
        field = schema.Set()
        self.assertIsInstance(field, schema.IterableField)
        self.assertIsNone(field.validate({1, 2}))
        with self.assertRaises(ValueError):
            field.validate([])

    def test_Dict(self):
        field = schema.Dict()
        self.assertIsInstance(field, schema.Field)
        self.assertEqual(field.type_, dict)
        self.assertEqual(field.serializer, UNSET)
        self.assertEqual(field.default, UNSET)
        self.assertEqual(field.key_type, UNSET)
        self.assertEqual(field.value_type, UNSET)
        self.assertEqual(field.size, UNSET)

        self.assertIsNone(field.validate({}))
        with self.assertRaises(ValueError):
            field.validate([])

        self.assertEqual(field.serialize({}), {})
        self.assertEqual(field.deserialize({}), {})

        field = schema.Dict(size=1)
        self.assertIsNone(field.validate({u'foo': u'bar'}))
        with self.assertRaises(ValueError):
            field.validate({})

        field = schema.Dict(key_type=schema.Int())
        self.assertIsNone(field.validate({1: u'foo'}))
        with self.assertRaises(ValueError):
            field.validate({u'1': u'foo'})

        field = schema.Dict(value_type=schema.Int())
        self.assertIsNone(field.validate({u'foo': 1}))
        with self.assertRaises(ValueError):
            field.validate({u'foo': u'1'})

        field = schema.Dict(serializer=schema.dict_serializer)
        self.assertEqual(
            field.serialize({u'foo': u'bar'}),
            u'foo,bar'
        )
        self.assertEqual(
            field.deserialize(u'foo,bar'),
            {u'foo': u'bar'}
        )
        with self.assertRaises(AttributeError if compat.IS_PY2 else TypeError):
            field.serialize({1: 1})

        field = schema.Dict(
            serializer=schema.dict_serializer,
            key_type=schema.Int(serializer=schema.int_serializer),
            value_type=schema.Int(serializer=schema.int_serializer)
        )
        self.assertEqual(field.serialize({1: 1}), u'1,1')
        self.assertEqual(field.deserialize(u'1,1'), {1: 1})

    def test_nested_Dict(self):
        field = schema.Dict(value_type=schema.Dict(size=1))
        self.assertIsNone(field.validate({u'foo': {u'1': u'1'}}))
        with self.assertRaises(ValueError):
            field.validate({u'foo': {}})

        field = schema.Dict(
            serializer=schema.dict_serializer,
            key_type=schema.Int(serializer=schema.int_serializer),
            value_type=schema.Dict(
                serializer=schema.dict_serializer,
                key_type=schema.Int(serializer=schema.int_serializer),
                value_type=schema.Int(serializer=schema.int_serializer)
            )
        )
        self.assertIsNone(field.validate({1: {1: 1}}))
        with self.assertRaises(ValueError):
            field.validate({1: 1})
        field.serialize({1: {1: 1}})
        self.assertEqual(field.serialize({1: {1: 1}}), u'1,1%2C1')
        self.assertEqual(field.deserialize(u'1,1%2C1'), {1: {1: 1}})

    def test_ODict(self):
        field = schema.ODict()
        self.assertIsInstance(field, schema.Field)
        self.assertEqual(field.type_, odict)
        self.assertEqual(field.serializer, UNSET)
        self.assertEqual(field.default, UNSET)
        self.assertEqual(field.key_type, UNSET)
        self.assertEqual(field.value_type, UNSET)
        self.assertEqual(field.size, UNSET)

        self.assertIsNone(field.validate(odict()))
        with self.assertRaises(ValueError):
            field.validate(dict)

        self.assertEqual(field.serialize(odict()), odict())
        self.assertEqual(field.deserialize(odict()), odict())

        field = schema.Dict(size=1)
        od = odict()
        od[u'foo'] = u'bar'
        self.assertIsNone(field.validate(od))
        with self.assertRaises(ValueError):
            field.validate(odict())

        field = schema.Dict(key_type=schema.Int())
        od = odict()
        od[1] = u'foo'
        self.assertIsNone(field.validate(od))
        with self.assertRaises(ValueError):
            od = odict()
            od[u'1'] = u'foo'
            field.validate(od)

        field = schema.Dict(value_type=schema.Int())
        od = odict()
        od[u'foo'] = 1
        self.assertIsNone(field.validate(od))
        with self.assertRaises(ValueError):
            od = odict()
            od[u'foo'] = u'1'
            field.validate(od)

        field = schema.Dict(serializer=schema.odict_serializer)
        od = odict()
        od[u'foo'] = u'bar'
        od[u'baz'] = u'bam'
        self.assertEqual(
            field.serialize(od),
            u'foo,bar;baz,bam'
        )
        self.assertEqual(field.deserialize(u'foo,bar;baz,bam'), od)
        with self.assertRaises(AttributeError if compat.IS_PY2 else TypeError):
            od = odict()
            od[1] = 1
            field.serialize(od)

    def test_Node(self):
        with self.assertRaises(TypeError):
            schema.Node()

        field = schema.Node(BaseNode)
        self.assertIsNone(field.validate(BaseNode()))
        with self.assertRaises(ValueError):
            field.validate({})

        parent = BaseNode()
        child = parent['child'] = BaseNode()
        self.assertEqual(field.serialize(child), child)
        with schema.scope_context(field, 'child', parent):
            self.assertEqual(field.deserialize(child), child)

        parent = BaseNode()
        with schema.scope_context(field, 'child', parent):
            child = field.deserialize('data')
        self.assertIsInstance(child, BaseNode)
        self.assertEqual(child.name, 'child')
        self.assertEqual(child.parent, parent)
        self.assertEqual(list(parent.keys()), ['child'])

        field = schema.Node(serializer=schema.NodeSerializer(BaseNode))
        self.assertEqual(field.type_, BaseNode)
        with schema.scope_context(field, 'sub', parent):
            child = field.deserialize('data')
        self.assertIsInstance(child, BaseNode)
        self.assertEqual(child.name, 'sub')
        self.assertEqual(child.parent, parent)
        self.assertEqual(sorted(parent.keys()), ['child', 'sub'])


class TestBehaviorsSchema(NodeTestCase):

    def test_Schema(self):
        @plumbing(Schema)
        class SchemaNode(BaseNode):
            child_constraints = None
            schema = {
                'int': schema.Int(),
                'float': schema.Float(default=1.),
                'str': schema.Str(),
                'bool': schema.Bool(default=False),
                'node': schema.Node(BaseNode)
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
        self.assertEqual(node['bool'], False)
        self.assertEqual(node['str'], UNSET)
        self.assertEqual(node['node'], UNSET)

        with self.assertRaises(ValueError):
            node['node'] = 'invalid type'
        child_node = node['node'] = BaseNode()
        self.assertEqual(node['node'], child_node)

        self.checkOutput("""
        <class 'node.tests.test_schema.SchemaNode'>: None
        __any: 'foo'
        __int: 0
        __<class 'node.base.BaseNode'>: node
        """, node.treerepr(prefix='_'))

    def test_SchemaAsAttributes(self):
        @plumbing(SchemaAsAttributes)
        class SchemaAsAttributesNode(BaseNode):
            schema = {
                'int': schema.Int(),
                'float': schema.Float(default=1.),
                'str': schema.Str(),
                'bool': schema.Bool(),
                'node': schema.Node(BaseNode)
            }

        node = SchemaAsAttributesNode()
        self.assertTrue(IAttributes.providedBy(node))
        self.assertTrue(ISchemaAsAttributes.providedBy(node))

        attrs = node.attrs
        self.assertTrue(INodeAttributes.providedBy(attrs))
        self.assertIsInstance(attrs, SchemaAttributes)
        self.assertEqual(
            sorted(iter(attrs)),
            ['bool', 'float', 'int', 'node', 'str']
        )

        attrs['int'] = 1
        attrs['float'] = 2.
        attrs['str'] = u'foo'
        attrs['bool'] = True
        child_node = attrs['node'] = BaseNode()
        self.assertEqual(node.storage, {
            'float': 2.,
            'int': 1,
            'str': u'foo',
            'bool': True,
            'node': child_node
        })

        self.checkOutput("""
        <class 'node.behaviors.schema.SchemaAttributes'>: __attrs__
        __bool: True
        __float: 2.0
        __int: 1
        __<class 'node.base.BaseNode'>: None
        __str: ...'foo'
        """, attrs.treerepr(prefix='_'))

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
        self.assertEqual(attrs.node, child_node)

        attrs.int = 2
        attrs.float = 3.
        attrs.str = u'bar'
        self.assertEqual(
            node.storage,
            {'float': 3., 'int': 2, 'str': u'bar', 'node': child_node}
        )

        attrs.float = UNSET
        self.assertEqual(attrs.float, 1.)
        self.assertEqual(
            node.storage,
            {'int': 2, 'str': u'bar', 'node': child_node}
        )

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

    def test_SchemaProperties(self):
        @plumbing(SchemaProperties)
        class SchemaPropertiesNode(BaseNode):
            child_constraints = None
            str_field = schema.Str()
            int_field = schema.Int(default=1)
            float_field = schema.Float(default=1.)
            bool_field = schema.Bool(default=True)
            uuid_field = schema.UUID(serializer=schema.uuid_serializer)
            node_field = schema.Node(BaseNode)

        self.assertEqual(
            sorted(SchemaPropertiesNode.__schema_members__),
            [
                'bool_field', 'float_field', 'int_field',
                'node_field', 'str_field', 'uuid_field'
            ]
        )
        self.assertEqual(SchemaPropertiesNode.str_field, UNSET)
        self.assertEqual(SchemaPropertiesNode.int_field, 1)
        self.assertEqual(SchemaPropertiesNode.float_field, 1.)
        self.assertEqual(SchemaPropertiesNode.bool_field, True)
        self.assertEqual(SchemaPropertiesNode.uuid_field, UNSET)
        self.assertEqual(SchemaPropertiesNode.node_field, UNSET)

        node = SchemaPropertiesNode()
        self.assertEqual(list(node.storage.keys()), [])
        self.assertEqual(node.str_field, UNSET)
        self.assertEqual(node.int_field, 1)
        self.assertEqual(node.float_field, 1.)
        self.assertEqual(node.bool_field, True)
        self.assertEqual(node.uuid_field, UNSET)
        self.assertEqual(node.node_field, UNSET)

        node.str_field = u'Value'
        node.int_field = 2
        node.float_field = 2.
        node.bool_field = False
        child_node = node.node_field = BaseNode()
        self.assertEqual(
            sorted(node.storage.keys()),
            [
                'bool_field', 'float_field',
                'int_field', 'node_field', 'str_field'
            ]
        )

        self.assertEqual(node.storage['str_field'], u'Value')
        self.assertEqual(node.storage['int_field'], 2)
        self.assertEqual(node.storage['float_field'], 2.)
        self.assertEqual(node.storage['bool_field'], False)
        self.assertEqual(node.storage['node_field'], child_node)

        self.checkOutput("""
        <class 'node.tests.test_schema.SchemaPropertiesNode'>: None
        __bool_field: False
        __float_field: 2.0
        __int_field: 2
        __<class 'node.base.BaseNode'>: node_field
        __str_field: ...'Value'
        __uuid_field: <UNSET>
        """, node.treerepr(prefix='_'))

        self.assertEqual(sorted(node.keys()), [])
        with self.assertRaises(KeyError):
            node['str_field']
        with self.assertRaises(KeyError):
            node['str_field'] = u'Value'
        with self.assertRaises(KeyError):
            del node['str_field']

        uid = uuid.UUID('733698c5-aaa9-4baa-9d62-35b627feee04')
        node.uuid_field = uid
        self.assertEqual(
            node.storage['uuid_field'],
            '733698c5-aaa9-4baa-9d62-35b627feee04'
        )
        self.assertEqual(node.uuid_field, uid)
        node.uuid_field = UNSET
        self.assertEqual(node.uuid_field, UNSET)
        with self.assertRaises(KeyError):
            node.storage['uuid_field']

        node['child'] = BaseNode()
        self.assertEqual(sorted(node.keys()), ['child'])

        @plumbing(SchemaProperties)
        class SchemaPropertiesDict(dict):
            str_field = schema.Str(default=u'Value')

        self.assertEqual(
            sorted(SchemaPropertiesDict.__schema_members__),
            ['str_field']
        )
        self.assertEqual(SchemaPropertiesDict.str_field, u'Value')

        dict_ = SchemaPropertiesDict()
        self.assertEqual(list(dict.keys(dict_)), [])
        self.assertEqual(dict_.str_field, u'Value')

        dict_.str_field = u'Other Value'
        self.assertEqual(list(dict.keys(dict_)), ['str_field'])
        self.assertEqual(dict.__getitem__(dict_, 'str_field'), u'Other Value')

        self.assertEqual(sorted(iter(dict_)), [])
        with self.assertRaises(KeyError):
            dict_['str_field']
        with self.assertRaises(KeyError):
            dict_['str_field'] = u'Value'
        with self.assertRaises(KeyError):
            del dict_['str_field']

        dict_['child'] = 1
        self.assertEqual(sorted(iter(dict_)), ['child'])

        self.assertTrue('int_field' in node.storage)
        del node.int_field
        self.assertFalse('int_field' in node.storage)
        self.assertEqual(node.int_field, 1)

        @plumbing(SchemaProperties)
        class SchemaPropertiesBase(BaseNode):
            field_1 = schema.Int()

        @plumbing(SchemaProperties)
        class SchemaPropertiesDerived(SchemaPropertiesBase):
            child_constraints = None
            field_2 = schema.Int()

        node = SchemaPropertiesDerived()
        with self.assertRaises(ValueError):
            node.field_1 = 1.
        with self.assertRaises(ValueError):
            node.field_2 = 2.
        node.field_1 = 1
        node.field_2 = 2

        self.assertEqual(node['field_1'], 1)
        self.assertEqual(node['field_2'], 2)
        self.checkOutput("""
        <class 'node.tests.test_schema.SchemaPropertiesDerived'>: None
        __field_1: 1
        __field_2: 2
        """, node.treerepr(prefix='_'))
