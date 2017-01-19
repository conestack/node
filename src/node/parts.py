# -*- coding: utf-8 -*-
from zope.deprecation import deprecated
import node.behaviors
import sys


sys.modules['node.parts'] = deprecated(node.behaviors, """
``node.parts`` is deprecated as of node 0.9.8 and will be removed in
node 1.0. Use ``node.behaviors`` instead.
""")
