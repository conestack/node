Thread locking for Nodes
========================

XXX: test has race conditions... still? added wait after thread start.
     if no longer appears, remove note.

A Dummy Node with _waiting flag for access collision check::

    >>> from node.base import BaseNode
    >>> class Dummy(BaseNode):
    ...     _waiting = False
    >>> dummy = Dummy()
    >>> global dummy

We need a thread implementation which checks for access collision::

    >>> import time
    >>> import threading
    >>> from threading import Thread
    >>> from node.locking import TreeLock
    >>> class TestThread(Thread):
    ...     _waited = False
    ...     def run(self):
    ...         while dummy._waiting:
    ...             self._waited = True
    ...             time.sleep(0.2)
    ...         lock = TreeLock(dummy)
    ...         lock.acquire()
    ...         dummy._waiting = True
    ...         time.sleep(0.1)
    ...         dummy._waiting = False
    ...         lock.release()
    ...     def is_alive(self):  # Python 2.5
    ...         return self.isAlive()

    >>> t1 = TestThread()
    >>> t2 = TestThread()
    >>> t1.start()
    >>> t2.start()
    >>> time.sleep(0.5)

We expect ``t1`` to proceed without waiting, ``t2`` waited some time::

    >>> t1._waited
    False
    
    >>> t2._waited
    True
    
    >>> while t1.is_alive() or t2.is_alive():
    ...     time.sleep(0.1)

Repeat test using with statement::

    >>> from __future__ import with_statement
    >>> class TestThread2_6(Thread):
    ...     _waited = False
    ...     def run(self):
    ...         while dummy._waiting:
    ...             self._waited = True
    ...             time.sleep(0.2)
    ...         with TreeLock(dummy):
    ...             dummy._waiting = True
    ...             time.sleep(0.1)
    ...             dummy._waiting = False
    
    >>> t1 = TestThread2_6()
    >>> t2 = TestThread2_6()
    >>> t1.start()
    >>> t2.start()
    >>> time.sleep(0.5)
    
    >>> if t1._waited:
    ...     raise Exception(u"t1 was not expected to wait")
    >>> if not t2._waited:
    ...     raise Exception(u"t2 was expected to wait")
    >>> while t1.is_alive() or t2.is_alive():
    ...     time.sleep(0.1)

Test locking decorator::

    >>> from node.locking import locktree
    >>> class LockingNode(BaseNode):
    ...     @locktree
    ...     def foo(self):
    ...         return 'fooed'
    
    >>> node = LockingNode()
    >>> node.foo()
    'fooed'
