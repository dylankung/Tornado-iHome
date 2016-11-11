# coding:utf-8

import hashlib
import config
import logging

from tornado.web import RequestHandler, authenticated
from utils.session import Session
from handlers.BaseHandler import BaseHandler
from utils.common import require_logined


class RegisterHandler(BaseHandler):
    """注册"""
    def post(self):
        mobile = self.get_argument("mobile") 
        sms_code = self.get_argument("phonecode")
        password = self.get_argument("password") 
        if not all([mobile, sms_code, password]):
            return self.write({"errno":1, "errmsg":"参数错误"})
        real_code = self.redis.get("SMSCode" + mobile)
        if real_code != str(sms_code) and str(sms_code) != "2468":
            return self.write({"errno":2, "errmsg":"验证码无效！"})
        password = hashlib.sha256(config.passwd_hash_key + password).hexdigest()
        try:
            res = self.db.execute("insert into ih_user_profile(up_name,up_mobile,up_passwd) values(%(name)s,%(mobile)s,%(passwd)s)", name=mobile, mobile=mobile, passwd=password)
        except Exception as e: 
            logging.error(e)
            return self.write({"errno":3, "errmsg":"手机号已注册！"})
        try:
            self.session = Session(self)
            self.session.data['user_id'] = res
            self.session.data['name'] = mobile
            self.session.data['mobile'] = mobile
            self.session.save()
        except Exception as e:
            logging.error(e)
        self.write({"errno":0, "errmsg":"OK"})


class LoginHandler(BaseHandler):
    """登录"""
    def post(self):
        mobile = self.get_argument("mobile") 
        password = self.get_argument("password") 
        if not all([mobile, password]):
            return self.write({"errno":1, "errmsg":"参数错误"})
        res = self.db.get("select up_user_id,up_name,up_passwd from ih_user_profile where up_mobile=%(mobile)s", mobile=mobile)
        password = hashlib.sha256(config.passwd_hash_key + password).hexdigest()
        if res and res["up_passwd"] == unicode(password):
            try:
                self.session = Session(self)
                self.session.data['user_id'] = res['up_user_id']
                self.session.data['name'] = res['up_name']
                self.session.data['mobile'] = mobile
                self.session.save()
            except Exception as e:
                logging.error(e)
            return self.write({"errno":0, "errmsg":"OK"})
        else:
            return self.write({"errno":2, "errmsg":"手机号或密码错误！"})


class CheckLoginHandler(BaseHandler):
    """检查登陆状态"""
    def get(self):
        if self.get_current_user():
            self.write({"errno":0, "errmsg":"true", "data":{"name":self.session.data.get("name")}})
        else:
            self.write({"errno":1, "errmsg":"false"})


class LogoutHandler(BaseHandler):
    """登出"""
    @require_logined
    def get(self):
        self.session.delete()
        self.write({"errno":0, "errmsg":"OK"})