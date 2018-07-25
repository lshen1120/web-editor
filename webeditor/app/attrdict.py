#!/usr/bin/env python
# -*- coding:utf-8 -*-
import copy


class AttrDict(dict):
    def __init__(self, seq=None, **kwargs):
        dict.__init__(self, seq or {}, **kwargs)

    def __getattr__(self, name):
        return self.get(name, self.get("__default", None))

    def __setattr__(self, name, value):
        self[name] = value

    def __getitem__(self, name):
        return self.get(name, self.get("__default", None))

    def __deepcopy__(self, memo):
        y = {}
        memo[id(self)] = y
        for key, value in self.iteritems():
            y[copy.deepcopy(key, memo)] = copy.deepcopy(value, memo)
        return y


def test_attr_dict_exist_attr():
    a = AttrDict()
    a.id = 1
    assert a.id == 1, 'a.id != 1'
    assert a.get('id') == 1, 'a.get("id") != 1'
    assert a['id'] == 1, 'a["id"] != 1'
    b = AttrDict(id=2)
    assert b.id == 2, 'b.id != 2'
    c = AttrDict({"id": 3})
    assert c.id == 3, 'c.id != 3'
    d = AttrDict(None)
    d.id = 4
    assert d.id == 4, 'd.id != 4'


def test_attr_dict_not_exist_attr():
    a = AttrDict()
    assert a.notexist is None, 'a.notexist is None'
    assert a['notexist'] is None, 'a["notexist"] not __default '


def test_attr_dict_not_exist_attr_default():
    a = AttrDict()
    a.__default = ''
    assert a.notexist == '', 'a.notexist not __default '
    assert a['notexist'] == '', 'a["notexist"] not __default '
    b = AttrDict(__default=0)
    assert b.notexist == 0, 'b.notexist not __default '


