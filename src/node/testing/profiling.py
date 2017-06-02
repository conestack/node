# -*- coding: utf-8 -*-
from node.base import Node
import cProfile


root = Node()


def create():
    global root
    for i in range(1, 10000):
        root[str(i)] = Node()


def delete():
    global root
    for i in range(1, 10000):
        del root[str(i)]


cProfile.run('create()')
cProfile.run('delete()')
