from node.base import BaseNode
from node.behaviors import Schema
from node.behaviors.schema import scope_field
from node.schema import Field
from node.tests import NodeTestCase
from node.utils import UNSET
from plumber import plumbing


class TestSchema(NodeTestCase):

    def test_Field(self):
        field = Field()

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

    def test_scope_field(self):
        field = Field()
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
                'int': Field(int)
            }

        node = SchemaNode()
        node['any'] = 'foo'
        self.assertRaises(ValueError, node.__setitem__, 'int', '1')
        node['int'] = 0

        self.checkOutput("""
        <class 'touch.infomap.tests.test_model_schema.SchemaNode'>: None
          any: 'foo'
          int: 0
        """, node.treerepr())

        self.assertEqual(node['any'], 'foo')
        self.assertEqual(node['int'], 0)
