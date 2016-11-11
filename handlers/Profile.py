# coding:utf-8

import logging

from .BaseHandler import BaseHandler
from utils.common import require_logined
from utils.image_storage import storage
from config import image_url_prefix

class ProfileHandler(BaseHandler):
    """个人信息"""
    @require_logined
    def get(self):
        user_id = self.session.data['user_id']
        try:
            ret = self.db.get("select up_name,up_mobile,up_avatar from ih_user_profile where up_user_id=%s", user_id)
        except Exception as e:
            logging.error(e)
            return self.write({"errno":1, "errmsg":"no data"})
        if ret["up_avatar"]:
            img_url = image_url_prefix + ret["up_avatar"]
        else:
            img_url = None
        self.write({"errno":0, "errmsg":"OK", "data":{"user_id":user_id, "name":ret["up_name"], "mobile":ret["up_mobile"], "avatar":img_url}})


class AvatarHandler(BaseHandler):
    """头像"""
    @require_logined
    def post(self):
        user_id = self.session.data["user_id"]
        avatar = self.request.files["avatar"][0]["body"]
        img_name = storage(avatar)
        if not img_name:
            return self.write({"errno":1, "errmsg":"qiniu error"})
        try:
            ret = self.db.execute("update ih_user_profile set up_avatar=%s where up_user_id=%s", img_name, user_id)
        except Exception as e:
            logging.error(e)
            return self.write({"errno":2, "errmsg":"upload failed"})
        img_url = image_url_prefix + img_name
        self.write({"errno":0, "errmsg":"OK", "url":img_url})


class NameHandler(BaseHandler):
    """用户名"""
    @require_logined
    def post(self):
        user_id = self.session.data["user_id"]
        name = self.json_args.get("name")
        if name in (None, ""):
            return self.write({"errno":1, "errmsg":"params error"})
        try:
            self.db.execute("update ih_user_profile set up_name=%s where up_user_id=%s", name, user_id)
        except Exception as e:
            logging.error(e)
            return self.write({"errno":2, "errmsg":"name has exist"})
        self.session.data["name"] = name
        self.session.save()
        self.write({"errno":0, "errmsg":"OK"}) 


class AuthHandler(BaseHandler):
    """实名认证"""
    @require_logined
    def get(self):
        user_id = self.session.data["user_id"]
        try:
            ret = self.db.get("select up_real_name,up_id_card from ih_user_profile where up_user_id=%s", user_id)
        except Exception as e:
            logging.error(e)
            return self.write({"errno":1, "errmsg":"get data failed"})
        if not ret:
            return self.write({"errno":2, "errmsg":"no data"})
        self.write({"errno":0, "errmsg":"OK", "data":{"real_name":ret.get("up_real_name", ""), "id_card":ret.get("up_id_card", "")}})

    @require_logined
    def post(self):
        user_id = self.session.data["user_id"]
        real_name = self.json_args.get("real_name")
        id_card = self.json_args.get("id_card")
        if real_name in (None, "") or id_card in (None, ""):
            return self.write({"errno":1, "errmsg":"params error"})
        try:
            self.db.execute("update ih_user_profile set up_real_name=%s,up_id_card=%s where up_user_id=%s", real_name, id_card, user_id)
        except Exception as e:
            logging.error(e)
            return self.write({"errno":2, "errmsg":"update failed"})
        self.write({"errno":0, "errmsg":"OK"})


