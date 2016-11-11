# coding:utf-8

from tornado.web import RequestHandler, authenticated, asynchronous
import re
import hashlib, binascii
import config
from utils import session
import os
from tornado import gen
from tornado.websocket import WebSocketHandler
import logging
import requests
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
import json
import pingpp

class IndexHandler(RequestHandler):

    def get(self):
        logging.error('file:%s,  this is error' % __file__)
        logging.info('this is info')
        logging.debug('aaaaaaaaaaaaaaaaa')
        logging.warning('this is warning')
        logging.debug('this is warning')
        # self.set_cookie("test_name","test_value")
        self.add_header("Set-Cookie","test_name1=test_value1; Path=/")
        self.render("index.html", is_login=False)

    def post(self):
        self.render("index.html")

class SearchHandler(RequestHandler):

    @gen.coroutine
    def get(self):
        keyword = self.get_argument('keyword')
        # 参数过滤遗留
        client = AsyncHTTPClient()
        url = "http://127.0.0.1:9200/test_database/houses/_search"
        data = '{"query":{"match":{"city":"%s"}}}' % keyword
        # 记得引入HTTPRequest
        req = HTTPRequest(url, method="GET", body=data,allow_nonstandard_methods=True)
        ret = yield client.fetch(req)
        self.finish(ret.body)


class LoginHandler(RequestHandler):
    def get(self):
        self.write("enter login html")

class BaseHandler(RequestHandler):
    def __init__(self, *args, **kwargs):
        super(BaseHandler, self).__init__(*args, **kwargs)
        self.session = session.Session(self.application.session_manager, self)

    def get_current_user(self):
        return self.session.get('name')

class ProfileHandler(BaseHandler):
    @authenticated
    def get(self):
        # self.write("进入个人主页")
        message = '%s entered profile page' % self.session.get('name', u'aaa')
        EnterProfilePageNotifyHandler.notify(message)
        logging.info(message)
        self.render('profile.html', is_login=True, user_name=self.session.get('name', u'亲'))

class OrdersHandler(BaseHandler):
    @authenticated
    def get(self):
        # self.write("进入个人主页")
        self.render('orders.html', is_login=True, user_name=self.session.get('name', u'亲'))


class RegisterHandler(RequestHandler):
    def get(self):
        self.render("register.html", error_msg="注册")

    def post(self):
        # req = self.request.body
        # logging.debug(req)
        # try:
        #     r = json.loads(req)
        # except Exception as e:
        #     logging.error(e)
        #     self.write('error')
        #     return
        name = self.get_argument('name')
        mobile = self.get_argument('mobile')
        passwd = self.get_argument('passwd1')

        # files = self.request.files
        # avatar_file = files.get('avatar')
        # upload_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
        # if avatar_file:
        #     avatar_file = avatar_file[0].get('body')
        #     file = open(os.path.join(upload_path, 'a1'), 'w+')
        #     file.write(avatar_file)
        #     file.close()
        if name in (None, '') or not re.match(r'^1[3|4|5|7|8]\d{9}$', mobile) or passwd in (None, ''):
            #self.write('{"status":"E01"}')
            self.render("register.html", error_msg="手机号格式错误!")
            return
        #passwd = binascii.hexlify(hashlib.pbkdf2_hmac('sha256', passwd, config.passwd_hash_key, 100000))
        passwd = hashlib.sha256( config.passwd_hash_key + passwd ).hexdigest()
        user = {'name':name, 'mobile':mobile, 'passwd':passwd}
        try:
            ret = self.application.db.users.insert(user)
        except Exception as e:
            self.render("register.html", error_msg="用户名已存在!")
        try:
            self.session = session.Session(self.application.session_manager, self)
            self.session['name'] = name
            self.session['mobile'] = mobile
            self.session.save()
        except Exception as e:
            logging.error("catch session error:" + e)
        #self.write('{"status":"00"}')
        self.redirect("/") 


class SyncHandler(RequestHandler):
    def get(self):
        os.system('ping -c 1 www.baidu.com')        
        self.finish('finished')


class AsyncHandler(RequestHandler):
    @gen.coroutine
    def get(self):
        ret = yield gen.Task(lambda x:os.system('ping -c 1 www.baidu.com'))
        # ret = yield gen.Task(self.task)
        # self.write(ret)
        self.finish('OK')

    @gen.coroutine
    def task(self):
        os.system('ping -c 1 www.baidu.com')
        return 'task finished'


# class LoginNotifyHandler(WebSocketHandler):
#     users = set()
#     def open(self):
#         LoginNotifyHandler.users.add(self)

#     def on_close(self):
#         LoginNotifyHandler.users.remove(self)

#     def on_message(self):
#         pass

#     @classmethod
#     def send_message(cls, message):
#         for user in cls.users:
#             try:
#                 user.write_message(message)
#             except Exception as e:
#                 print e

class HouseHandler(RequestHandler):
    def get(self, hid1, hid2):
        hid3 = self.get_argument('hid3', 'a')
        self.write('this is hid: %s hid2: %s hid3:%s' % (hid1, hid2, hid3))

class TaobaoIPHandler(RequestHandler):
    def get(self):
        url = 'http://ip.taobao.com/service/getIpInfo.php?ip=210.75.225.254'
        ret = requests.get(url)
        self.write(str(dir(ret)))
        # self.write(ret.content)

class AsyncTaobaoIPHandler(RequestHandler):

    # @asynchronous
    # def get(self):
    #     url = 'http://ip.taobao.com/service/getIpInfo.php?ip=210.75.225.254'
    #     client = AsyncHTTPClient()
    #     client.fetch(url, self.callback)
    #     self.write('after fetch')

    # def callback(self, response):
    #     self.write(str(dir(response)))
    #     self.write(response.body)
    #     self.finish('finished')

    @gen.coroutine
    def get(self):
        url = 'http://ip.taobao.com/service/getIpInfo.php?ip=210.75.225.254'
        client = AsyncHTTPClient()
    #     self.write('after fetch')
        response = yield client.fetch(url)
        self.write('after fetch')
        self.write(response.body)
        self.finish('finished')

class EnterProfilePageNotifyHandler(WebSocketHandler):
    users = set()
    # a = [2,1,3,1]
    # list(set(a)).sort(a.index)
    def open(self):
        EnterProfilePageNotifyHandler.users.add(self) 
        logging.error(EnterProfilePageNotifyHandler.users)

    def on_close(self):
        EnterProfilePageNotifyHandler.users.remove(self)

    def on_message(self):
        pass

    @classmethod
    def notify(cls, message):
        logging.error(cls.users)
        for user in cls.users:
            user.write_message(message)
            logging.error(message)

class OrderHandler(RequestHandler):
    """下单接口"""
    def post(self):
        order_id = self.get_argument('order_id')
        subject = self.get_argument('subject')
        body = self.get_argument('body')
        amount = self.get_argument('amount')
        channel = self.get_argument('channel')
        client_ip = self.request.remote_ip
        # 参数校验
        # 订单数据存放到数据库中
        try:
            pingpp.api_key = 'sk_test_GaLOiLivXXXTr9Wbn5eXj1yH'
            charge = pingpp.Charge.create(
                order_no=order_id,
                amount=float(amount)*100, #订单总金额, 人民币单位：分（如订单总金额为 1 元，此处请填 100）
                app=dict(id='app_rfnvzTLS8yD09enD'),
                channel=channel,
                currency='cny',
                client_ip=client_ip,
                subject=subject,
                body=body,
                extra={
                    "success_url":"http://"+ self.request.host +"/orders"
                }
            )
        except Exception as e:
            logging.error(e)
            self.write('error')
            return
        self.write(charge)