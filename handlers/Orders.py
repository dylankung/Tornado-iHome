# coding:utf-8

import logging
import datetime

from .BaseHandler import BaseHandler
from utils.common import require_logined
from config import image_url_prefix

class OrderHandler(BaseHandler):
    """订单"""
    @require_logined
    def post(self):
        """提交订单"""
        user_id = self.session.data["user_id"]
        house_id = self.json_args.get("house_id")
        start_date = self.json_args.get("start_date")
        end_date = self.json_args.get("end_date")
        if not all((house_id, start_date, end_date)):
            return self.write({"errno":1, "errmsg":"params error"}) 
        # 查询房屋是否存在
        try:
            house = self.db.get("select hi_price from ih_house_info where hi_house_id=%s", house_id)
        except Exception as e:
            logging.error(e)
            return self.write({"errno":2, "errmsg":"get house error"})
        if not house:
            return self.write({"errno":3, "errmsg":"no data"})
        # 判断日期是否可以
        days = (datetime.datetime.strptime(end_date, "%Y-%m-%d") - datetime.datetime.strptime(start_date, "%Y-%m-%d")).days + 1
        if days<=0:
            return self.write({"errno":4, "errmsg":"date params error"}) 
        try:
            ret = self.db.get("select count(*) counts from ih_order_info where oi_house_id=%(house_id)s and oi_begin_date<%(end_date)s and oi_end_date>%(start_date)s", house_id=house_id, end_date=end_date, start_date=start_date)
        except Exception as e:
            logging.error(e)
            return self.write({"errno":5, "errmsg":"get date error"})
        if ret["counts"] > 0:
            return self.write({"errno":6, "errmsg":"serve date error"})
        amount = days * house["hi_price"]
        try:
            self.db.execute("insert into ih_order_info(oi_user_id,oi_house_id,oi_begin_date,oi_end_date,oi_days,oi_house_price,oi_amount) values(%(user_id)s,%(house_id)s,%(begin_date)s,%(end_date)s,%(days)s,%(price)s,%(amount)s);", user_id=user_id, house_id=house_id, begin_date=start_date, end_date=end_date, days=days, price=house["hi_price"], amount=amount)
        except Exception as e:
            logging.error(e)
            return self.write({"errno":7, "errmsg":"save data error"})
        self.write({"errno":0, "errmsg":"OK"})


class MyOrdersHandler(BaseHandler):
    """我的订单"""
    @require_logined
    def get(self):
        user_id = self.session.data["user_id"]
        role = self.get_argument("role", "")
        try:
            if "landlord" == role:
                ret = self.db.query("select oi_order_id,hi_title,hi_index_image_url,oi_begin_date,oi_end_date,oi_ctime,oi_days,oi_amount,oi_status from ih_order_info inner join ih_house_info on oi_house_id=hi_house_id where hi_user_id=%s", user_id)
            else:
                ret = self.db.query("select oi_order_id,hi_title,hi_index_image_url,oi_begin_date,oi_end_date,oi_ctime,oi_days,oi_amount,oi_status from ih_order_info inner join ih_house_info on oi_house_id=hi_house_id where oi_user_id=%s", user_id)
        except Exception as e:
            logging.error(e)
            return self.write({"errno":1, "errmsg":"get data error"})
        orders = []
        if ret:
            for l in ret:
                order = {
                    "order_id":l["oi_order_id"],
                    "title":l["hi_title"],
                    "img_url":image_url_prefix + l["hi_index_image_url"] if l["hi_index_image_url"] else "",
                    "start_date":l["oi_begin_date"].strftime("%Y-%m-%d"),
                    "end_date":l["oi_end_date"].strftime("%Y-%m-%d"),
                    "ctime":l["oi_ctime"].strftime("%Y-%m-%d %H:%M:%S"),
                    "days":l["oi_days"],
                    "amount":l["oi_amount"],
                    "status":l["oi_status"]
                }
                orders.append(order)
        self.write({"errno":0, "errmsg":"OK", "orders":orders})
