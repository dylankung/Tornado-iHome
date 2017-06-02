# coding:utf-8

import os

from handlers.base import StaticFileHandler
from handlers import verfiycode, passport, profile, houses, orders


ihome_api_urls = [
    # 用户管理功能部分
    (r'^/api/imagecode?', verfiycode.ImageCodeHandler),  # 图片验证码
    (r'^/api/smscode?', verfiycode.SMSCodeHandler),  # 短信验证码
    (r'^/api/register$', passport.RegisterHandler),  # 用户注册
    (r'^/api/login$', passport.LoginHandler),  # 登录
    (r'^/api/check_login$', passport.CheckLoginHandler),  # 判断用户是否登录
    (r'^/api/logout$', passport.LogoutHandler),  # 登出
    (r'^/api/profile$', profile.ProfileHandler),  # 获取个人信息
    (r'^/api/profile/avatar$', profile.AvatarHandler),  # 修改头像
    (r'^/api/profile/name$', profile.NameHandler),  # 修改用户名
    (r'^/api/profile/auth$', profile.AuthHandler),  # 实名认证信息

    # 房屋管理功能部分
    (r'^/api/house/info$', houses.HouseInfoHandler),  # 房屋详细信息
    (r'^/api/house/image$', houses.HouseImageHandler),  # 房屋图片
    (r'^/api/house/area$', houses.AreaInfoHandler),  # 房屋城区信息
    (r'^/api/house/my$', houses.MyHousesHandler),  # 用户发布的房源信息
    (r'^/api/house/index$', houses.IndexHandler),  # 首页展示的房屋信息
    (r'^/api/house/list$', houses.HouseListRedisHandler),  # 房源筛选列表数据

    # 订单管理功能部分
    (r'^/api/order$', orders.OrderHandler),  # 下单
    (r'^/api/order/my$', orders.MyOrdersHandler),  # 我的订单，作为房客与房东同时适用
    (r'^/api/order/accept$', orders.AcceptOrderHandler),  # 接单
    (r'^/api/order/reject$', orders.RejectOrderHandler),  # 拒单
    (r'^/api/order/comment$', orders.OrderCommentHandler),  # 评价
]

urls = []
urls.extend(ihome_api_urls)
urls.extend([
    (r'^/(.*)$', StaticFileHandler, {'path': os.path.join(os.path.dirname(__file__), 'html'),
                                     'default_filename': 'index.html'}),
])   

