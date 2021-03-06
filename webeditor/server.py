# -*- coding: utf-8 -*-

import logging
import os
import signal
import socket

import sys
import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.httpclient
import tornado.iostream
import tornado.tcpclient

import logging.config

from tornado.log import LogFormatter
import config
from app import handlers, logger, utils

import sys
reload(sys)
sys.setdefaultencoding("utf-8")


tornado_options = {
    'port': 8000,
    'workers': 3,
    'debug': False,
    'socket_timeout': 3,
    'backlog': 1024
}

if len(sys.argv) > 1:
    port = int(sys.argv[1])
    tornado_options['port'] = port

addrs = socket.getaddrinfo(socket.gethostname(), None)
ips = {}
for item in addrs:
    ip = item[4][0]
    if ':' not in ip and ip not in ips:
        print('http://' + ip + ':' + str(tornado_options['port']))
        ips[ip] = 1


def init_tornado_options():
    for k in tornado_options:
        v = tornado_options[k]
        tornado.options.define(k, default=v, type=type(v))
    tornado.options.parse_command_line()
    return tornado.options.options


def load_routings(router):
    modules_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'modules'))
    modules = []
    sys.path.insert(0, modules_path)
    module_names = os.listdir(modules_path)
    for mod_name in module_names:
        # check the module name is an available module
        if not os.path.isfile(os.path.join(modules_path, mod_name, 'routing.py')):
            continue
        routing = utils.load_module(".".join([mod_name, "routing"]), modules_path)
        if hasattr(routing, 'routing_table'):
            router.extend(routing.routing_table)
        modules.append(mod_name)
    sys.path.pop(0)
    return modules


def start_server():
    options = init_tornado_options()
    # init socket options
    socket.setdefaulttimeout(options.socket_timeout)
    # server settings for application
    app_settings = {
        'debug': options.debug,
        'template_path': os.path.join(os.path.dirname(__file__), 'template'),
        'static_path': os.path.join(os.path.dirname(__file__), 'static'),
        'cookie_secret': 'ngYrl3h4TRGF9KM6zb5x2Q/v5sH8T0BbsOisjQIL95Q='
    }
    # cookie_secret generated by "base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes)"

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    log_file = 'sys.log'
    # timelog = logging.handlers.TimedRotatingFileHandler(log_file, 'midnight', 1, 0)
    # logger.addHandler(timelog)

    datefmt = '%Y-%m-%d %H:%M:%S'
    fmt = '%(color)s[%(levelname)1.1s %(asctime)s %(module)s:%(lineno)d]%(end_color)s %(message)s'
    formatter = LogFormatter(color=True, datefmt=datefmt, fmt=fmt)
    root_log = logging.getLogger()
    for logHandler in root_log.handlers:
        logHandler.setFormatter(formatter)

    logging.info('options: {}'.format(options.items()))

    # set default handler, just response 404
    router = list()
    # load routing
    load_routings(router=router)
    # else
    router.append((ur'/.*', handlers.APINotFoundHandler))
    # setting to handlers
    handlers.APIBaseHandler.static_config.update(config.config)

    def shutdown(sig, frame):
        logging.info("shutting down on signal:%s", sig)
        tornado.ioloop.IOLoop.instance().stop()

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    # create tornado application and httpserver
    application = tornado.web.Application(router, **app_settings)
    httpserver = tornado.httpserver.HTTPServer(application)
    httpserver.bind(options.port, backlog=options.backlog)
    httpserver.start(1 if options.debug else options.workers)
    # ioloop start
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    start_server()
