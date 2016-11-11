# coding:utf-8

import json

from tornado.web import RequestHandler
from utils.session import Session

class BaseHandler(RequestHandler):
    """请求处理基类"""

    def get_current_user(self):
        self.session = Session(self)
        return self.session.data.get('name')

    @property
    def db(self):
        return self.application.db

    @property
    def redis(self):
        return self.application.redis

    def prepare(self):
        if self.request.headers.get("Content-Type", "").startswith("application/json"):
            self.json_args = json.loads(self.request.body)
        else:
            self.json_args = None
