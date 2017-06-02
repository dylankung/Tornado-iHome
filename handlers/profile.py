# coding:utf-8

import logging

from handlers.base import BaseHandler
from utils.common import require_logined
from utils.image_storage import storage
from config import image_url_prefix
from utils.response_code import RET


class ProfileHandler(BaseHandler):
    """个人信息"""
    @require_logined
    def get(self):
        """获取个人信息"""
        user_id = self.session.data['user_id']
        # 查询数据库获取个人信息
        try:
            ret = self.db.get("select up_name,up_mobile,up_avatar from ih_user_profile where up_user_id=%s", user_id)
        except Exception as e:
            logging.error(e)
            return self.write({"errno": RET.DBERR, "errmsg": "no data"})

        # 将头像的url地址补充完整
        if ret["up_avatar"]:
            img_url = image_url_prefix + ret["up_avatar"]
        else:
            img_url = None
        self.write({"errno": RET.OK, "errmsg": "OK", "data": {"user_id": user_id, "name": ret["up_name"],
                                                              "mobile": ret["up_mobile"], "avatar": img_url}})


class AvatarHandler(BaseHandler):
    """头像"""
    @require_logined
    def post(self):
        user_id = self.session.data["user_id"]

        # 获取头像图片数据, 返回一个列表
        avatar = self.request.files.get("avatar")
        if not avatar:
            return self.write(dict(errno=RET.PARAMERR, errmsg="未传头像"))
        try:
            img_name = storage(avatar[0].body)
        except Exception as e:
            logging.error(e)
            return self.write(dict(errno=RET.THIRDERR, errmsg="上传头像失败"))

        # 操作数据库，保存头像信息
        sql = "update ih_user_profile set up_avatar=%s where up_user_id=%s"
        try:
            self.db.execute_rowcount(sql, img_name, user_id)
        except Exception as e:
            logging.error(e)
            return self.write({"errno": RET.DBERR, "errmsg": "upload failed"})

        img_url = image_url_prefix + img_name
        self.write({"errno": RET.OK, "errmsg": "OK", "url": img_url})


class NameHandler(BaseHandler):
    """用户名"""
    @require_logined
    def post(self):
        # 从session中获取用户身份,user_id
        user_id = self.session.data["user_id"]

        # 获取用户想要设置的用户名
        name = self.json_args.get("name")

        # 判断name是否传了，并且不应为空字符串
        # if name == None or "" == name:
        if name in (None, ""):
            return self.write({"errno": RET.PARAMERR, "errmsg": "params error"})

        # 保存用户昵称name，并同时判断name是否重复（利用数据库的唯一索引)
        try:
            self.db.execute_rowcount("update ih_user_profile set up_name=%s where up_user_id=%s", name, user_id)
        except Exception as e:
            logging.error(e)
            return self.write({"errno": RET.DBERR, "errmsg": "name has exist"})

        # 修改session数据中的name字段，并保存到redis中
        self.session.data["name"] = name
        try:
            self.session.save()
        except Exception as e:
            logging.error(e)
        self.write({"errno": RET.OK, "errmsg": "OK"})


class AuthHandler(BaseHandler):
    """实名认证"""
    @require_logined
    def get(self):
        """获取用户的实名认证信息"""
        user_id = self.session.data["user_id"]

        # 在数据库中查询信息
        try:
            ret = self.db.get("select up_real_name,up_id_card from ih_user_profile where up_user_id=%s", user_id)
        except Exception as e:
            logging.error(e)
            return self.write({"errno": RET.DBERR, "errmsg": "get data failed"})
        if not ret:
            return self.write({"errno": RET.NODATA, "errmsg": "no data"})
        self.write({"errno": RET.OK, "errmsg": "OK", "data": {"real_name": ret.get("up_real_name", ""),
                                                              "id_card": ret.get("up_id_card", "")}})

    @require_logined
    def post(self):
        """保存实名认证信息"""
        user_id = self.session.data["user_id"]
        real_name = self.json_args.get("real_name")
        id_card = self.json_args.get("id_card")
        # 参数校验
        if real_name in (None, "") or id_card in (None, ""):
            return self.write({"errno": RET.PARAMERR, "errmsg": "params error"})
        try:
            self.db.execute_rowcount("update ih_user_profile set up_real_name=%s,up_id_card=%s where up_user_id=%s",
                                     real_name, id_card, user_id)
        except Exception as e:
            logging.error(e)
            return self.write({"errno": RET.DBERR, "errmsg": "update failed"})
        self.write({"errno": RET.OK, "errmsg": "OK"})


