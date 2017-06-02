from node import locking
from node.base import BaseNode
from node.tests import patch
from node.tests import unittest
import threading


class MockLock(object):

    def __init__(self):
        self._lock = threading.RLock()
        self.count = 0

    def acquire(self):
        self._lock.acquire()
        self.count += 1

    def release(self):
        self._lock.release()
        self.count -= 1


class TestLocking(unittest.TestCase):

    @patch(locking, 'RLock', MockLock)
    def test_TreeLock(self):
        node = BaseNode()
        lock = locking.TreeLock(node)
        self.assertEqual(lock.lock.count, 0)
        lock.acquire()
        self.assertEqual(lock.lock.count, 1)
        lock.acquire()
        self.assertEqual(lock.lock.count, 2)
        lock.release()
        self.assertEqual(lock.lock.count, 1)
        lock.release()
        self.assertEqual(lock.lock.count, 0)

    @patch(locking, 'RLock', MockLock)
    def test_with_TreeLock(self):
        node = BaseNode()
        lock = locking.TreeLock(node)
        with lock:
            self.assertEqual(lock.lock.count, 1)
        self.assertEqual(lock.lock.count, 0)

    @patch(locking, 'RLock', MockLock)
    def test_locktree(self):
        testcase = self

        class LockingNode(BaseNode):
            @locking.locktree
            def locked(self):
                testcase.assertEqual(self.root._treelock.count, 1)

        node = LockingNode()
        self.assertFalse(hasattr(node.root, '_treelock'))
        node.locked()
        self.assertEqual(node.root._treelock.count, 0)
