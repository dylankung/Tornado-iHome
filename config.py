# coding:utf-8

import os


# Mysql配置参数
mysql_options = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "mysql",
    "database": "ihome"
}

# Redis配置参数
redis_options = {
    'host': '127.0.0.1',
    'port': 6379,
}

# Application类用到的配置参数
settings = {
    'static_path': os.path.join(os.path.dirname(__file__), 'static'),
    'cookie_secret': '0Q1AKOKTQHqaa+N80XhYW7KCGskOUE2snCW06UIxXgI=',
    'xsrf_cookies': True,
    'debug': True,
}

# 密码加密密钥
passwd_hash_key = "F3fv87mzTI6fKbP13gUNZI+eZrL1VEzguyX1+AVsRdI="

# 日志文件
log_path = os.path.join(os.path.dirname(__file__), 'logs/log')

# 日志等级
log_level = "debug"

# 七牛空间域名
image_url_prefix = "http://o91qujnqh.bkt.clouddn.com/"
