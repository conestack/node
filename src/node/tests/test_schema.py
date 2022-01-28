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
import uuid


class TestObject(object):

    def __init__(self, value):
        self.value = value


class TestSchema(NodeTestCase):

    def test_scope_field(self):
        field = schema.Field(str)
        parent = object()
        with schema.scope_field(field, 'name', parent):
            self.assertEqual(field.name, 'name')
            self.assertTrue(field.parent is parent)
        self.assertEqual(field.name, None)
        self.assertEqual(field.parent, None)

    def test_Field(self):
        field = schema.Field(str)
        self.assertEqual(field.type_, str)
        self.assertEqual(field.default, UNSET)
        self.assertEqual(field.dump, UNSET)
        self.assertEqual(field.load, UNSET)

        self.assertIsNone(field.validate('value'))
        with self.assertRaises(ValueError):
            field.validate(1)

        self.assertEqual(field.serialize('value'), 'value')
        self.assertEqual(field.deserialize('value'), 'value')

        field = schema.Field(uuid.UUID, dump=str)
        self.assertEqual(field.type_, uuid.UUID)
        self.assertEqual(field.dump, str)
        self.assertEqual(field.load, uuid.UUID)

        uid = uuid.uuid4()
        self.assertIsNone(field.validate(uid))
        with self.assertRaises(ValueError):
            field.validate(1)

        self.assertEqual(field.serialize(uid), str(uid))
        self.assertEqual(field.deserialize(str(uid)), uid)

        def load(value):
            return uuid.UUID(value)

        field = schema.Field(uuid.UUID, dump=str, load=load)
        self.assertEqual(field.type_, uuid.UUID)
        self.assertEqual(field.dump, str)
        self.assertEqual(field.load, load)

        self.assertIsNone(field.validate(uid))
        with self.assertRaises(ValueError):
            field.validate(1)

        self.assertEqual(field.serialize(uid), str(uid))
        self.assertEqual(field.deserialize(str(uid)), uid)

        class TestSerializer(schema.Serializer):
            def dump(self, value):
                return 'serialized'
            def load(self, value):
                return 'deserialized'

        serializer = TestSerializer()
        field = schema.Field(str, serializer=serializer)
        self.assertEqual(field.dump, serializer.dump)
        self.assertEqual(field.load, serializer.load)
        self.assertEqual(field.serialize(''), 'serialized')
        self.assertEqual(field.deserialize(''), 'deserialized')

        parent = object()
        field.set_scope('name', parent)
        self.assertEqual(field.name, 'name')
        self.assertTrue(field.parent is parent)

        field.reset_scope()
        self.assertEqual(field.name, None)
        self.assertEqual(field.parent, None)

    def test_IterableField(self):
        field = schema.IterableField(list)
        self.assertIsInstance(field, schema.Field)
        self.assertEqual(field.type_, list)
        self.assertEqual(field.dump, UNSET)
        self.assertEqual(field.load, UNSET)
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

        field = schema.IterableField(
            list,
            dump=schema.iter_join,
            load=schema.iter_split
        )
        self.assertEqual(field.serialize(['a', 'b', 'c']), b'a,b,c')
        self.assertEqual(field.deserialize(b'a,b,c'), ['a', 'b', 'c'])
        with self.assertRaises(TypeError):
            field.serialize([1, 2, 3])

        field = schema.IterableField(tuple, serializer=schema.iter_serializer)
        self.assertEqual(field.serialize(('a', 'b', 'c')), b'a,b,c')
        self.assertEqual(field.deserialize(b'a,b,c'), ('a', 'b', 'c'))

        field = schema.IterableField(
            tuple,
            serializer=schema.iter_serializer,
            value_type=schema.Int(dump=str)
        )
        self.assertEqual(field.serialize((1, 2, 3)), b'1,2,3')
        self.assertEqual(field.deserialize(b'1,2,3'), (1, 2, 3))

        field = schema.IterableField(
            set,
            serializer=schema.iter_serializer,
            value_type=schema.UUID(dump=str)
        )
        uid = uuid.UUID('1f4be432-a693-44bd-9eb8-e0b8d3aec82d')
        self.assertEqual(
            field.serialize({uid}),
            b'1f4be432-a693-44bd-9eb8-e0b8d3aec82d'
        )
        self.assertEqual(
            field.deserialize(b'1f4be432-a693-44bd-9eb8-e0b8d3aec82d'),
            {uid}
        )

    def test_nested_IterableField(self):
        field = schema.IterableField(list, value_type=schema.List(size=1))
        self.assertIsNone(field.validate([[1]]))
        with self.assertRaises(ValueError):
            field.validate([[1, 2]])

        field = schema.IterableField(
            list,
            serializer=schema.iter_serializer,
            value_type=schema.Tuple(
                serializer=schema.iter_serializer,
                value_type=schema.Int(dump=str)
            )
        )
        self.assertIsNone(field.validate([(1, 2), (3,)]))
        with self.assertRaises(ValueError):
            field.validate([(1, 2), 3])
        self.assertEqual(field.serialize([(1, 2), (3,)]), b'1%2C2,3')
        self.assertEqual(field.deserialize(b'1%2C2,3'), [(1, 2), (3,)])

        field = schema.IterableField(
            list,
            serializer=schema.iter_serializer,
            value_type=schema.Set(
                serializer=schema.iter_serializer,
                value_type=schema.Tuple(
                    serializer=schema.iter_serializer,
                    value_type=schema.Int(dump=str)
                )
            )
        )
        self.assertIsNone(field.validate([{(1, 2)}, {(3,)}]))
        with self.assertRaises(ValueError):
            field.validate([{(1, 2)}, {3}])
        self.assertEqual(field.serialize([{(1, 2)}, {(3,)}]), b'1%252C2,3')
        self.assertEqual(field.deserialize(b'1%252C2,3'), [{(1, 2)}, {(3,)}])

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
            field.validate('1234')

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
        self.assertEqual(field.dump, UNSET)
        self.assertEqual(field.load, UNSET)
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
        self.assertIsNone(field.validate({'foo': 'bar'}))
        with self.assertRaises(ValueError):
            field.validate({})

        field = schema.Dict(key_type=schema.Int())
        self.assertIsNone(field.validate({1: 'foo'}))
        with self.assertRaises(ValueError):
            field.validate({'1': 'foo'})

        field = schema.Dict(value_type=schema.Int())
        self.assertIsNone(field.validate({'foo': 1}))
        with self.assertRaises(ValueError):
            field.validate({'foo': '1'})

        field = schema.Dict(dump=schema.dict_join, load=schema.dict_split)
        self.assertEqual(
            field.serialize({'foo': 'bar', 'baz': 'bam'}),
            b'foo,bar;baz,bam'
        )
        self.assertEqual(
            field.deserialize(b'foo,bar;baz,bam'),
            {'foo': 'bar', 'baz': 'bam'}
        )
        with self.assertRaises(TypeError):
            field.serialize({1: 1})

    def test_nested_Dict(self):
        field = schema.Dict(value_type=schema.Dict(size=1))
        self.assertIsNone(field.validate({'foo': {'1': '1'}}))
        with self.assertRaises(ValueError):
            field.validate({'foo': {}})

        field = schema.Dict(
            serializer=schema.dict_serializer,
            key_type=schema.Int(dump=str),
            value_type=schema.Dict(
                serializer=schema.dict_serializer,
                key_type=schema.Int(dump=str),
                value_type=schema.Int(dump=str)
            )
        )
        self.assertIsNone(field.validate({1: {1: 1}}))
        with self.assertRaises(ValueError):
            field.validate({1: 1})
        self.assertEqual(field.serialize({1: {1: 1}}), b'1,1%2C1')
        self.assertEqual(field.deserialize(b'1,1%2C1'), {1: {1: 1}})

    def test_ODict(self):
        field = schema.ODict()
        self.assertIsInstance(field, schema.Field)
        self.assertEqual(field.type_, odict)
        self.assertEqual(field.dump, UNSET)
        self.assertEqual(field.load, UNSET)
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
        od['foo'] = 'bar'
        self.assertIsNone(field.validate(od))
        with self.assertRaises(ValueError):
            field.validate(odict())

        field = schema.Dict(key_type=schema.Int())
        od = odict()
        od[1] = 'foo'
        self.assertIsNone(field.validate(od))
        with self.assertRaises(ValueError):
            od = odict()
            od['1'] = 'foo'
            field.validate(od)

        field = schema.Dict(value_type=schema.Int())
        od = odict()
        od['foo'] = 1
        self.assertIsNone(field.validate(od))
        with self.assertRaises(ValueError):
            od = odict()
            od['foo'] = '1'
            field.validate(od)

        field = schema.Dict(dump=schema.dict_join, load=schema.odict_split)
        od = odict()
        od['foo'] = 'bar'
        od['baz'] = 'bam'
        self.assertEqual(
            field.serialize(od),
            b'foo,bar;baz,bam'
        )
        self.assertEqual(field.deserialize(b'foo,bar;baz,bam'), od)
        with self.assertRaises(TypeError):
            od = odict()
            od[1] = 1
            field.serialize(od)

    def test_Node(self):
        field = schema.Node(BaseNode)
        self.assertIsNone(field.validate(BaseNode()))
        with self.assertRaises(ValueError):
            field.validate({})

        parent = BaseNode()
        child = parent['child'] = BaseNode()
        self.assertEqual(field.serialize(child), child)
        with schema.scope_field(field, 'child', parent):
            self.assertEqual(field.deserialize(child), child)

        parent = BaseNode()
        with schema.scope_field(field, 'child', parent):
            child = field.deserialize('data')
        self.assertIsInstance(child, BaseNode)
        self.assertEqual(child.name, 'child')
        self.assertEqual(child.parent, parent)

        def load(value, name, parent):
            child = parent[name] = BaseNode()
            return child

        field = schema.Node(BaseNode, load=load)
        with schema.scope_field(field, 'sub', parent):
            child = field.deserialize('data')
        self.assertIsInstance(child, BaseNode)
        self.assertEqual(child.name, 'sub')
        self.assertEqual(child.parent, parent)
        self.assertEqual(list(parent.keys()), ['sub'])

    def test_Serializer(self):
        with self.assertRaises(TypeError):
            schema.Serializer()

    def test_IterJoin(self):
        join = schema.IterJoin()
        self.assertEqual(join((u'a', u'b', u'c')), b'a,b,c')
        self.assertEqual(join([u'a', u'b', u'c']), b'a,b,c')
        self.assertEqual(join([u'a,', u'b', u'c']), b'a%2C,b,c')
        self.assertIsInstance(schema.iter_join, schema.IterJoin)

    def test_IterSplit(self):
        split = schema.IterSplit()
        self.assertEqual(split(b'a,b,c'), [u'a', u'b', u'c'])
        self.assertEqual(split(b'a%2C,b,c'), [u'a,', u'b', u'c'])
        self.assertIsInstance(schema.iter_split, schema.IterSplit)

    def test_IterSerializer(self):
        serializer = schema.IterSerializer()
        self.assertIsInstance(serializer, schema.Serializer)
        self.assertIsInstance(serializer.dumper, schema.IterJoin)
        self.assertIsInstance(serializer.loader, schema.IterSplit)
        self.assertIsInstance(schema.iter_serializer, schema.IterSerializer)
        self.assertEqual(serializer.dump((u'a', u'b', u'c')), b'a,b,c')
        self.assertEqual(serializer.load(b'a,b,c'), [u'a', u'b', u'c'])

    def test_DictJoin(self):
        join = schema.DictJoin()
        self.assertEqual(join({'foo': 'bar', 'baz': 'bam'}), b'foo,bar;baz,bam')
        self.assertEqual(join({'foo,': 'bar;'}), b'foo%2C,bar%3B')
        self.assertIsInstance(schema.dict_join, schema.DictJoin)

    def test_DictSplit(self):
        split = schema.DictSplit()
        self.assertEqual(split(b'foo,bar;baz,bam'), {'foo': 'bar', 'baz': 'bam'})
        self.assertEqual(split(b'foo%2C,bar%3B'), {'foo,': 'bar;'})
        self.assertIsInstance(schema.dict_split, schema.DictSplit)

        self.assertIsInstance(schema.odict_split, schema.DictSplit)
        self.assertEqual(schema.odict_split.type_, odict)
        od = odict()
        od['foo'] = 'bar'
        od['baz'] = 'bam'
        self.assertEqual(schema.odict_split(b'foo,bar;baz,bam'), od)

    def test_DictSerializer(self):
        serializer = schema.DictSerializer()
        self.assertIsInstance(serializer, schema.Serializer)
        self.assertIsInstance(serializer.dumper, schema.DictJoin)
        self.assertIsInstance(serializer.loader, schema.DictSplit)
        self.assertIsInstance(schema.dict_serializer, schema.DictSerializer)
        self.assertEqual(
            serializer.dump({'foo': 'bar', 'baz': 'bam'}),
            b'foo,bar;baz,bam'
        )
        self.assertEqual(
            serializer.load(b'foo,bar;baz,bam'),
            {'foo': 'bar', 'baz': 'bam'}
        )

        self.assertIsInstance(schema.odict_serializer, schema.DictSerializer)
        self.assertEqual(schema.odict_serializer.loader.type_, odict)
        od = odict()
        od['foo'] = 'bar'
        od['baz'] = 'bam'
        self.assertEqual(
            schema.odict_serializer.load(b'foo,bar;baz,bam'),
            od
        )

    def test_Base64Serializer(self):
        serializer = schema.Base64Serializer()
        self.assertIsInstance(serializer, schema.Serializer)
        self.assertIsInstance(schema.base64_serializer, schema.Base64Serializer)
        self.assertEqual(serializer.dump(u'value'), b'dmFsdWU=')
        self.assertEqual(serializer.load(b'dmFsdWU='), u'value')

        serializer = schema.Base64Serializer(type_=bytes)
        self.assertEqual(serializer.dump(b'value'), b'dmFsdWU=')
        self.assertEqual(serializer.load(b'dmFsdWU='), b'value')

    def test_JSONSerializer(self):
        serializer = schema.JSONSerializer()
        self.assertIsInstance(serializer, schema.Serializer)
        self.assertIsInstance(schema.json_serializer, schema.JSONSerializer)
        self.assertEqual(serializer.dump({'foo': 'bar'}), '{"foo": "bar"}')
        self.assertEqual(serializer.load('{"foo": "bar"}'), {'foo': 'bar'})

    def test_PickleSerializer(self):
        serializer = schema.PickleSerializer()
        self.assertIsInstance(serializer, schema.Serializer)
        self.assertIsInstance(schema.pickle_serializer, schema.PickleSerializer)
        data = (
            b'\x80\x03cnode.tests.test_schema\nTestObject\nq\x00)'
            b'\x81q\x01}q\x02X\x05\x00\x00\x00valueq\x03h\x03sb.'
        )
        self.assertEqual(serializer.dump(TestObject('value')), data)
        obj = serializer.load(data)
        self.assertIsInstance(obj, TestObject)
        self.assertEqual(obj.value, 'value')

    def test_Schema(self):
        @plumbing(Schema)
        class SchemaNode(BaseNode):
            allow_non_node_children = True
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
        __str: 'foo'
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
            allow_non_node_children = True
            str_field = schema.Str()
            int_field = schema.Int(default=1)
            float_field = schema.Float(default=1.)
            bool_field = schema.Bool(default=True)
            uuid_field = schema.UUID(dump=str)
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
        __str_field: 'Value'
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
