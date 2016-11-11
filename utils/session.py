#coding:utf-8

import json
import uuid
import config

class Session(object):

    def __init__(self, request_handler):
        """
        request_handler - 请求处理类对象实例
        sid - session_id
        data - session数据, 字典类型
        """
        self.request_handler = request_handler
        self.sid = request_handler.get_secure_cookie("session_id")
        if self.sid:
            json_data = request_handler.redis.get("sess_%s" % self.sid)
            if json_data:
                self.data = json.loads(json_data)
            else:
                self.sid = uuid.uuid4().get_hex()
                self.data = {}
        else:
            self.sid = uuid.uuid4().get_hex()
            self.data = {}

    def save(self):
        """保存"""
        self.request_handler.set_secure_cookie("session_id", self.sid) # cookie默认有效期30天
        json_data = json.dumps(self.data) 
        self.request_handler.redis.setex("sess_%s" % self.sid, config.session_expires_seconds, json_data)
        
    def delete(self):
        """清除"""
        self.request_handler.clear_cookie("session_id")
        self.request_handler.redis.delete("sess_%s" % self.sid)