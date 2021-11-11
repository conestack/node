from node.behaviors import BoundContext
from node.interfaces import IBoundContext
from node.tests import NodeTestCase
from plumber import plumbing
from zope.interface import implementer
from zope.interface import Interface


class IBoundInterface(Interface):
    pass


class BoundClass(object):
    pass


@plumbing(BoundContext)
class ContextAware(object):

    @classmethod
    def unbind_context(cls):
        cls.__bound_context_interfaces__ = ()
        cls.__bound_context_classes__ = ()


class TestContext(NodeTestCase):

    def test_BoundContext_bind_context(self):
        self.assertEqual(ContextAware.__bound_context_interfaces__, ())
        self.assertEqual(ContextAware.__bound_context_classes__, ())

        ContextAware.bind_context(None)
        self.assertEqual(ContextAware.__bound_context_interfaces__, ())
        self.assertEqual(ContextAware.__bound_context_classes__, ())

        ca = ContextAware()
        self.assertTrue(IBoundContext.providedBy(ca))

        ContextAware.bind_context(IBoundInterface)
        self.assertEqual(
            ContextAware.__bound_context_interfaces__,
            (IBoundInterface,)
        )
        self.assertEqual(ContextAware.__bound_context_classes__, ())

        ContextAware.unbind_context()

        ContextAware.bind_context(BoundClass)
        self.assertEqual(ContextAware.__bound_context_interfaces__, ())
        self.assertEqual(
            ContextAware.__bound_context_classes__,
            (BoundClass,)
        )

        ContextAware.unbind_context()
        ContextAware.bind_context(IBoundInterface, BoundClass)
        self.assertEqual(
            ContextAware.__bound_context_interfaces__,
            (IBoundInterface,)
        )
        self.assertEqual(
            ContextAware.__bound_context_classes__,
            (BoundClass,)
        )

        with self.assertRaises(RuntimeError):
            ContextAware.bind_context(object)

        ContextAware.unbind_context()
        with self.assertRaises(ValueError):
            ContextAware.bind_context(lambda: 1)

    def test_BoundContext_context_matches(self):
        @implementer(IBoundInterface)
        class BoundInterface(object):
            pass

        ContextAware.unbind_context()
        inst = ContextAware()
        self.assertTrue(inst.context_matches(object()))

        ContextAware.bind_context(BoundClass)
        inst = ContextAware()
        self.assertFalse(inst.context_matches(object()))
        self.assertTrue(inst.context_matches(BoundClass()))

        ContextAware.unbind_context()
        ContextAware.bind_context(IBoundInterface)
        inst = ContextAware()
        self.assertFalse(inst.context_matches(object()))
        self.assertTrue(inst.context_matches(BoundInterface()))

        ContextAware.unbind_context()
        ContextAware.bind_context(IBoundInterface, BoundClass)
        inst = ContextAware()
        self.assertFalse(inst.context_matches(object()))
        self.assertTrue(inst.context_matches(BoundClass()))
        self.assertTrue(inst.context_matches(BoundInterface()))
