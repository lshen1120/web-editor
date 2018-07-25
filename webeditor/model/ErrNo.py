#!/usr/bin/env python
# -*- coding:utf-8 -*-

class ErrNo(object):
    SYS_ERR = -1
    NO_ERR = 0
    SECRET_ERR = 40001

    ERRORS = {
        SYS_ERR: u"系统繁忙，此时请开发者稍候再试",
        NO_ERR: u"请求成功",

    }

    ERROR_NO_LIST = [key for key in sorted(ERRORS.keys())]
