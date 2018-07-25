#!/usr/bin/env python
# -*- coding: utf-8 -*-

from apis import *

routing_table = [
    (r'/', IndexHandler),
    (r'/editor', FileEditorHandler),
    (r'/tree', TreeHandler),
    (r'/resources', ResourceHandler),
]
