# coding:utf-8

import json
import tornado.web

from utils.session import Session


class BaseHandler(tornado.web.RequestHandler):
    """请求处理基类"""

    def get_current_user(self):
        """
        判断用户是否登录成功
        :return: 登录成功返回用户的昵称，否则返回None
        """
        self.session = Session(self)
        return self.session.data.get('name')

    @property
    def db(self):
        """提供对数据库连接实例db的属性操作"""
        return self.application.db

    @property
    def redis(self):
        """提供对Redis连接实例redis的属性操作"""
        return self.application.redis

    def prepare(self):
        """预处理，解析请求中的json数据"""
        if self.request.headers.get("Content-Type", "").startswith("application/json"):
            self.json_args = json.loads(self.request.body)
        else:
            self.json_args = {}

    def set_default_headers(self):
        """设置默认的响应报文中的header，默认返回json格式数据"""
        self.set_header("Content-Type", "application/json; charset=UTF-8")


class StaticFileHandler(tornado.web.StaticFileHandler):
    """提供静态文件的处理类，补充设置xsrf cookie的功能"""

    def __init__(self, *args, **kwargs):
        super(StaticFileHandler, self).__init__(*args, **kwargs)
        # 通过获取xsrf_token属性，可以自动设置xsrf cookie
        self.xsrf_token