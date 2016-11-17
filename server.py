# coding:utf-8

import tornado.web
import tornado.httpserver
import tornado.ioloop
import tornado.options
import config
import redis
import torndb

from tornado.options import options, define
from urls import urls
from utils import session

define("port", default=8000, help="run on the given port", type=int)

class Application(tornado.web.Application):
    def __init__(self):
        settings = config.settings
        self.redis = redis.StrictRedis(host=config.redis_options['redis_host'], port=config.redis_options['redis_port'])
        self.db = torndb.Connection(
            host = config.mysql_options['host'],
            user = config.mysql_options['user'],
            password = config.mysql_options['password'],
            database = config.mysql_options['database']
        )
        super(Application, self).__init__(urls, **settings)


def main():
    options.log_file_prefix = config.log_path
    options.logging = 'debug'
    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.current().start() 


if __name__ == '__main__':
    main()