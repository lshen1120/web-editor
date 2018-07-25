# -*- coding:utf-8 -*-

import json
import logging

import tornado.web
import tornado.options
from attrdict import AttrDict

from exception import ApiException
from view_helper import *
# import model.ErrNo as ErrNo
import webeditor.model.ErrNo as ErrNo

ErrNo = ErrNo.ErrNo


class APIBaseHandler(tornado.web.RequestHandler):
    static_config = AttrDict()
    IS_DEBUG = True
    LOGIN_ACCOUNT_ID = 'login_account_id'
    LOG_INFO = {}
    # fix request arguments not all utf8 characters
    _ARG_DEFAULT = []

    def __init__(self, application, request, **kwargs):
        super(APIBaseHandler, self).__init__(application, request, **kwargs)
        self.config = APIBaseHandler.static_config

    def initialize(self, **kwargs):
        if kwargs:
            self.LOG_INFO = {
                "desc": kwargs.get("desc", ""),
                "oper_type": kwargs.get("oper", ''),
                "obj_type": kwargs.get("obj", 0)
            }

    def get(self, *args, **kwargs):
        self.write_json(error=ErrNo.REQ_MUST_POST, status=200)

    def post(self, *args, **kwargs):
        self.write_json(error=ErrNo.REQ_MUST_GET, status=200)

    def write_json(self, data=None, error=ErrNo.NO_ERR, status=200):
        """return an contacts response in the proper output format"""
        self.set_status(status)
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        if data is None:
            data = json.dumps({'error': error})
        else:
            data = json.dumps({'error': error, 'data': data}, indent=2, ensure_ascii=False)
        callback = self.get_argument('callback', '')
        if callback:  # jsonp supported
            data = '{}({})'.format(callback, data)
        if error != ErrNo.NO_ERR or status != 200:
            logging.error('======output data=======:\n%s', data)
        else:
            logging.debug('======output data=======:\n%s', data)
        self.write(data)

    def write_ok(self):
        self.write_json()

    def get_int_argument(self, name, default=0):
        val = self.get_argument(name, default)
        try:
            return int(float(val))
        except:
            return int(default)

    def get_page_index(self):
        return self.get_int_argument('page_index', 1)

    def get_page_size(self):
        return self.get_int_argument('page_size', 14)

    def get_search_field(self):
        return self.get_argument('search_field', '')

    def get_search_value(self):
        return self.get_argument('search_value', '')

    @property
    def client_ip(self):
        if not hasattr(self, '_real_ip'):
            self._real_ip = self.request.headers.get('X-Real-Ip', self.request.remote_ip)
        return self._real_ip

    def get_user_agent(self):
        """
        :rtype: str
        """
        return self.get_header('User-Agent', None)

    def get_header(self, header_name, header_value=None):
        return self.request.headers.get(header_name, header_value)

    def check_required_params(self, *params):
        """
        校验必填的参数
        :param params: 必填的参数名
        :return: 如果所有必填参数都有设置，返回True，否则返回False,并且向客户端输出必填的参数列表
        """
        required = []
        for param in params:
            v = self.get_argument(param, '')
            if v == '':
                required.append(param)
        if len(required) > 0:
            raise ApiException({'data': required, 'error': ErrNo.PARAMS_INVALID})

    def get_file(self, part_name='data'):
        """
        获取上传的文件数据，0为数据整体，1为file_name
        :param part_name: 上传表单中 file 的名称
        :return: 文件数据
        """
        return self.request.files[part_name][0]

    def write_error(self, status_code, **kwargs):

        logging.error('error::{}'.format(kwargs))

        exception = None
        if 'exc_info' in kwargs:
            exception = kwargs['exc_info'][1]

        self.set_status(status_code)
        self.set_header('Content-Type', 'application/json; charset=UTF-8')
        if exception is None or not isinstance(exception, ApiException):
            self.finish(json.dumps({'error': status_code}))
            return

        # LWException 处理
        error_code = exception.error
        self.finish(json.dumps({'error': error_code}))

    def get_cruser_id(self):
        context = self.current_user
        if context.isUser:
            return context.user.id
        else:
            return 0

    def get_creator_info(self):
        context = self.current_user
        if context.isUser:
            return 1, context.user.id
        return 2, context.account.id

    def get_login_name(self):
        context = self.current_user
        if context.account:
            return context.account.get('account_name', '')
        if context.user:
            return context.user.get('nick_name', '')
        return ''

    def get_page_objs(self, objs, pager):
        if objs is None or len(objs) == 0:
            return objs

        results = []
        for i in range(pager.get_page_index_start(), pager.get_page_index_end() + 1):
            results.append(objs[i])

        return results


class HTMLBaseHandler(APIBaseHandler):
    def get(self, *args, **kwargs):
        self.render("404.html")

    def post(self, *args, **kwargs):
        self.render("404.html")

    def write_error(self, status_code, **kwargs):

        logging.error('error::{}'.format(kwargs))

        exception = None
        if 'exc_info' in kwargs:
            exception = kwargs['exc_info'][1]

        # 非管理员
        if exception is None or not isinstance(exception, ApiException):
            error_info = """
                    <html><title>{code}: {message}</title><body><p>服务器暂时无法响应...</p><p>{code}: {message}</p></body></html>
                    """.format(code=status_code, message='内部错误')
            self.finish(error_info)
            return

        # 抛出LWException，特殊处理
        error_code = exception.error
        error_info = "<html><title>错误码：{code}</title><body><p>服务器暂时无法响应...</p><p>错误码：{code}</p>".format(code=error_code)
        if error_code in [ErrNo.ACCOUNT_INVALID, ErrNo.ACCOUNT_PASSWD_ERROR, ErrNo.ACCOUNT_MIMIC_EDIT]:
            error_info += "<p>错误描述：{}</p>".format(utils.encode_utf8(ErrNo.ERRORS.get(error_code, '')))

        error_info += "<a href='javascript:history.back(-1)'>返回</a></body></html>"
        self.finish(error_info)

    def get_login_url(self):
        return '/login'

    def forbidden_if_client_invalid(self):
        # TODO
        # self.render("admin/login.html")
        return

class APIErrorHandler(tornado.web.ErrorHandler):
    def initialize(self, status_code, *args, **kwargs):
        tornado.web.ErrorHandler.initialize(self, status_code)


class APINotFoundHandler(APIErrorHandler):
    def initialize(self, *args, **kwargs):
        APIErrorHandler.initialize(self, 404, *args, **kwargs)

    def send_error(self, status_code=404, **kwargs):
        self.set_status(status_code)
        self.set_header('Content-Type', 'application/json; charset=UTF-8')
        self.finish(json.dumps({'error': ErrNo.NOT_FOUND}))
