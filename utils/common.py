# coding:utf-8

import functools

from utils.response_code import RET


def require_logined(fun):
    """要求用户必须登录的装饰器"""
    @functools.wraps(fun)
    def wrapper(request_handler, *args, **kwargs):
        # 根据get_current_user方法判读用户是否验证成功，即是否登录
        # 若验证不成功，返回错误信息
        if not request_handler.get_current_user():
            return request_handler.write({"errno":RET.SESSIONERR, "errmsg": "用户未登录"})
        # 若验证成功
        else:
            fun(request_handler, *args, **kwargs)
    return wrapper
