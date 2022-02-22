from threading import RLock


class TreeLock(object):

    def __init__(self, node):
        root = node.root
        self.lock = getattr(root, '_treelock', None)
        if self.lock is None:
            self.lock = root._treelock = RLock()

    def acquire(self):
        self.lock.acquire()

    __enter__ = acquire

    def release(self):
        self.lock.release()

    def __exit__(self, type, value, traceback):
        self.release()


def locktree(fn):
    """Decorator for locking of a whole method."""
    def _locktree_decorator(self, *args, **kwargs):
        lock = TreeLock(self)
        lock.acquire()
        try:
            result = fn(self, *args, **kwargs)
        finally:
            lock.release()
        return result
    return _locktree_decorator
