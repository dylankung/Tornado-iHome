# coding:utf-8

import tornado.web
import tornado.httpserver
import tornado.options
import tornado.ioloop
import torndb
import redis

from urls import urls
from config import settings, mysql_options, redis_options, log_path, log_level
from tornado.options import options

tornado.options.define("port", default=8000, type=int, help="在指定端口启动")


class Application(tornado.web.Application):
    """定制的Application，用来补充db数据库实例"""
    def __init__(self, *args, **kwargs):
        # 调用执行父类tornado.web.Application的初始化方法
        super(Application, self).__init__(*args, **kwargs)

        # 构造数据库连接对象
        self.db = torndb.Connection(**mysql_options)

        # 构造redis连接实例
        self.redis = redis.StrictRedis(**redis_options)


def main():
    # 设置日志文件保存目录
    options.log_file_prefix = log_path
    # 设置日志输出登记
    options.logging = log_level
    # 设置日志文件切割大小
    # options.log_file_max_size = 128

    # 转换命令行参数
    tornado.options.parse_command_line()

    # 构造web应用对象
    app = Application(urls, **settings)
    # 构造服务器对象
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()

if __name__ == '__main__':
    main()