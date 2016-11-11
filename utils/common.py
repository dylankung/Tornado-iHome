# coding:utf-8

import functools

def require_logined(fun):
    @functools.wraps(fun)
    def wrapper(request_handler, *args, **kwargs):
        if not request_handler.get_current_user():
            return request_handler.write({"errno":-1, "errmsg":"requrie logined"})
        else:
            fun(request_handler, *args, **kwargs)
    return wrapper
