# coding:utf-8

import os

mysql_options = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "mysql",
    "database": "ihome"
}

redis_options = {
    'redis_host':'127.0.0.1',
    'redis_port':6379,
}

settings = {
    'template_path': os.path.join(os.path.dirname(__file__), 'template'),
    'static_path': os.path.join(os.path.dirname(__file__), 'static'),
    'cookie_secret':'0Q1AKOKTQHqaa+N80XhYW7KCGskOUE2snCW06UIxXgI=',
    'xsrf_cookies':False,
    'login_url':'/login',
    'debug':True,
}

passwd_hash_key = "ihome@$^*"
session_expires_seconds = 86400 # session有效期，秒，24小时

log_path = os.path.join(os.path.dirname(__file__), 'logs/log')

image_url_prefix = "http://o91qujnqh.bkt.clouddn.com/"