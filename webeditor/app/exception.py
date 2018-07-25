#!/usr/bin/env python
# -*- coding:utf-8 -*-
import tornado.web
import json


class ApiException(tornado.web.HTTPError):
    def __init__(self, result, error=-1):
        tornado.web.HTTPError.__init__(self, 200)
        self.result = result

        if error == -1:
            try:
                if isinstance(self.result, json):
                    result_json = result
                else:
                    result_json = json.loads(result)
                self.error = result_json.get('error', -1)
            except:
                pass
        else:
            self.error = error
