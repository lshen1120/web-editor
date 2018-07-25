#!/usr/bin/env python
# -*- coding:utf-8 -*-


import logging
import sys
import os
from logging.handlers import WatchedFileHandler

req_id = 0


def currentframe():
    try:
        raise Exception
    except:
        return sys.exc_info()[2].tb_frame.f_back


if hasattr(sys, '_getframe'): currentframe = lambda: sys._getframe(3)


class AppLogger(logging.Logger):
    def __init__(self, name):
        super(AppLogger, self).__init__(name, logging.DEBUG)

    def findCaller(self):
        f = currentframe()
        if f is not None:
            f = f.f_back
        rv = "(unknown file)", 0, "(unknown function)"
        if __file__[-4:].lower() in ['.pyc', '.pyo']:
            _srcfile = __file__[:-4] + '.py'
        else:
            _srcfile = __file__
        while hasattr(f, "f_code"):
            co = f.f_code
            filename = os.path.normcase(co.co_filename)
            if filename == os.path.normcase(_srcfile):
                f = f.f_back
                continue
            rv = (co.co_filename, f.f_lineno, co.co_name)
            break
        return rv


def get_logger(filename='/tmp/log.txt', level=logging.DEBUG):
    log_formatter = logging.Formatter(
        "%(asctime)s[%(levelname)s][%(name)s][%(module)s-%(lineno)s]-%(process)d %(message)s")
    root_logger = logging.getLogger()
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(log_formatter)
    root_logger.handlers = []
    root_logger.addHandler(console_handler)
    logging.setLoggerClass(AppLogger)
    greenbay_logger = logging.getLogger('app')
    file_handler = WatchedFileHandler(filename)
    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(level)
    greenbay_logger.handlers = []
    greenbay_logger.addHandler(file_handler)
    greenbay_logger.setLevel(level=level)
    return greenbay_logger


def get_scripts_logger(filename='/tmp/log.txt', level=logging.DEBUG):
    log_formatter = logging.Formatter(
        "%(asctime)s[%(levelname)s][%(name)s][%(module)s-%(lineno)s]-%(process)d %(message)s")
    root_logger = logging.getLogger('app')
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(log_formatter)
    root_logger.handlers = []
    root_logger.addHandler(console_handler)
    file_handler = WatchedFileHandler(filename)
    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(level)
    root_logger.addHandler(file_handler)
    root_logger.setLevel(level=level)


def log(level, msg, *args, **kwargs):
    logging.getLogger('app').log(level, msg, *args, **kwargs)


def critical(msg, *args, **kwargs):
    msg = "{}\t{}".format(req_id, msg)
    log(logging.CRITICAL, msg, *args, **kwargs)


fatal = critical


def error(msg, *args, **kwargs):
    msg = "{}\t{}".format(req_id, msg)
    log(logging.ERROR, msg, *args, **kwargs)


def exception(msg, *args, **kwargs):
    msg = "{}\t{}".format(req_id, msg)
    kwargs['exc_info'] = 1
    error(msg, *args, **kwargs)


def warning(msg, *args, **kwargs):
    msg = "{}\t{}".format(req_id, msg)
    log(logging.WARN, msg, *args, **kwargs)


warn = warning


def info(msg, *args, **kwargs):
    msg = "{}\t{}".format(req_id, msg)
    log(logging.INFO, msg, *args, **kwargs)


def debug(msg, *args, **kwargs):
    msg = "{}\t{}".format(req_id, msg)
    log(logging.DEBUG, msg, *args, **kwargs)


def log_request(handler):
    if handler.get_status() < 400:
        log_method = info
    elif handler.get_status() < 500:
        log_method = warning
    else:
        log_method = error
    request_time = 1000.0 * handler.request.request_time()
    log_method("%s %d %.2fms", "REQUEST_TIME", handler.get_status(), request_time)


def set_req_id(id):
    global req_id
    req_id = id
