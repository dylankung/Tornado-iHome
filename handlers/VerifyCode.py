# coding:utf-8

from tornado.web import RequestHandler
from utils.captcha.captcha import captcha
from lib.yuntongxun import CCP
from .BaseHandler import BaseHandler

import logging
import config
import constants
import types
import random

class ImageCodeHandler(BaseHandler):
    """图片验证码"""
    def get(self):
        pre_code_id = self.get_argument("p")
        cur_code_id = self.get_argument("c")
        try:
            name, text, image = captcha.generate_captcha()
        except Exception as e:
            logging.error(e)
        if pre_code_id:
            self.redis.delete("ImageCode" + pre_code_id)
        self.redis.setex("ImageCode" + cur_code_id, constants.IMAGE_CODE_VALIDITY, text)
        self.set_header("Content-Type", "image/jpg")
        self.write(image)


class SMSCodeHandler(BaseHandler):
    """手机验证码"""
    def get(self):
        mobile = self.get_argument("mobile")
        image_code = self.get_argument("code")
        image_code_id = self.get_argument("codeId")
        if not all([mobile, image_code, image_code_id]):
            return self.write({"errno":1, "errmsg":"参数错误"}) 
        real_image_code = self.application.redis.get("ImageCode" + image_code_id)
        if not real_image_code:
            return self.write({"errno":2, "errmsg":"图片验证码已过期"})
        if not isinstance(image_code, types.StringType):
            image_code = str(image_code)
        if not isinstance(real_image_code, types.StringType):
            real_image_code = str(real_image_code)
        if image_code.lower() != real_image_code.lower():
            self.redis.delete("ImageCode" + image_code_id)
            return self.write({"errno":3, "errmsg":"图片验证码错误"})
        res = self.db.get("select count(*) counts from ih_user_profile where up_mobile=%(mobile)s", mobile=mobile)
        if 0 != res['counts']:
            return self.write({"errno":4, "errmsg":"该手机号已存在"})    
        sms_code = '%04d' % random.randint(0, 10000) 
        self.redis.setex("SMSCode" + mobile, constants.SMS_CODE_VALIDITY, sms_code)
        try:
            CCP.ccp.sendTemplateSMS(mobile, [sms_code, 5], 1)
        except Exception as e:
            logging.error(e)
        self.write({"errno":0, "errmsg":"OK"})

