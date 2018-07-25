# -*- coding:utf-8 -*-

import os

from webeditor.app.attrdict import AttrDict

config = {
    'tornado_options': {
        'port': 8000,
        'workers': 10,
        'debug': True,
        'socket_timeout': 3,
        'backlog': 1024
    }
}

# config.update(local_config.config)

config = AttrDict(config)
for name, value in config.iteritems():
    config[name] = AttrDict(value) if isinstance(value, dict) else value
