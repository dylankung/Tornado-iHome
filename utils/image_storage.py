# -*- coding: utf-8 -*-

import qiniu.config
import logging

from qiniu import Auth, put_data, etag, urlsafe_base64_encode

#需要填写你的 Access Key 和 Secret Key
access_key = 'uzc59bVURbUbazey9vrexXKocNKBUN8NuLijk57N'
secret_key = '-9lenw28jU2REojvGkcsEPWk5Nm9V2HIVqb5Nkts'

#要上传的空间
bucket_name = 'ihome'


def storage(data):
    """
    七牛云存储上传文件接口
    """
    if not data:
        return None
    try:
        #构建鉴权对象
        q = Auth(access_key, secret_key)

        #生成上传 Token，可以指定过期时间等
        token = q.upload_token(bucket_name)

        ret, info = put_data(token, None, data)

    except Exception as e:
        logging.error(e)
        return None

    if info and info.status_code != 200:
        return None

    return ret["key"]


if __name__ == '__main__':
    file_name = raw_input("输入上传的文件")
    file = open(file_name, 'rb')
    data = file.read()
    storage(data)

