# coding:utf-8

from handlers.BaseHandler import *
from tornado.web import StaticFileHandler
from config import settings
from handlers import VerifyCode, Passport, Profile, House

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
]

mis_api_urls = [
]

urls = [
    (r'^/()$', StaticFileHandler, {'path':os.path.join(settings['static_path'], 'html/ihome'), 'default_filename':'index.html'}),
    (r'^/view/(.+)$', StaticFileHandler, {'path':os.path.join(settings['static_path'], 'html/ihome')}),
    (r'^/mis/()$', StaticFileHandler, {'path':os.path.join(settings['static_path'], 'html/mis'), 'default_filename':'index.html'}),
    (r'^/mis/view/(.+)$', StaticFileHandler, {'path':os.path.join(settings['static_path'], 'html/mis')}),
]

urls.extend(ihome_api_urls)
urls.extend(mis_api_urls)
