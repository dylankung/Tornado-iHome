# coding:utf-8

from handlers.BaseHandler import *
from tornado.web import StaticFileHandler
from handlers import VerifyCode, Passport, Profile, House, Orders

import os


ihome_api_urls = [
    (r'^/api/imagecode?', VerifyCode.ImageCodeHandler),
    (r'^/api/smscode?', VerifyCode.SMSCodeHandler),
    (r'^/api/register$', Passport.RegisterHandler),
    (r'^/api/login$', Passport.LoginHandler),
    (r'^/api/check_login$', Passport.CheckLoginHandler),
    (r'^/api/logout$', Passport.LogoutHandler),
    (r'^/api/profile$', Profile.ProfileHandler),
    (r'^/api/profile/avatar$', Profile.AvatarHandler),
    (r'^/api/profile/name$', Profile.NameHandler),
    (r'^/api/profile/auth$', Profile.AuthHandler),
    (r'^/api/house/info$', House.HouseInfoHandler),
    (r'^/api/house/image$', House.HouseImageHandler),
    (r'^/api/house/area$', House.HouseAreaHandler),
    (r'^/api/house/my$', House.MyHousesHandler),
    (r'^/api/house/index$', House.IndexHandler),
    (r'^/api/house/list$', House.HouseListHandler),
    (r'^/api/order$', Orders.OrderHandler),
    (r'^/api/order/my$', Orders.MyOrdersHandler),
]

mis_api_urls = [
]

urls = []
urls.extend(ihome_api_urls)
urls.extend(mis_api_urls)
urls.extend([
    (r'^/(.*)$', StaticFileHandler, {'path':os.path.join(os.path.dirname(__file__), 'html'), 'default_filename':'index.html'}),
])   

