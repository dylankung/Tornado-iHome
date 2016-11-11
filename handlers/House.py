# coding:utf-8

import logging

from .BaseHandler import BaseHandler
from utils.common import require_logined
from utils.image_storage import storage
from config import image_url_prefix

class HouseAreaHandler(BaseHandler):
    """房屋区域"""
    @require_logined
    def get(self):
        try:
            ret = self.db.query("select ai_area_id,ai_name from ih_area_info;")
        except Exception as e:
            logging.error(e)
            return self.write({"errno":1, "errmsg":"get data error"})
        area_data = []
        for area in ret:
            area_data.append(dict(area_id=area["ai_area_id"], name=area["ai_name"]))
        self.write({"errno":0, "errmsg":"OK", "data":area_data})


class HouseInfoHandler(BaseHandler):
    """单一房屋"""
    def get(self):
        pass

    @require_logined
    def post(self):
        user_id = self.session.data["user_id"]
        # {"title":"","price":"","area_id":"1","address":"","room_count":"","acreage":"","unit":"","capacity":"","beds":"","deposit":"","min_days":"","max_days":"","facility":["7","8"]}"
        title = self.json_args.get("title")
        price = self.json_args.get("price")
        area_id = self.json_args.get("area_id")
        address = self.json_args.get("address")
        room_count = self.json_args.get("room_count")
        acreage = self.json_args.get("acreage")
        unit = self.json_args.get("unit")
        capacity = self.json_args.get("capacity")
        beds = self.json_args.get("beds")
        deposit = self.json_args.get("deposit")
        min_days = self.json_args.get("min_days")
        max_days = self.json_args.get("max_days")
        if not all((title, price, area_id, address, room_count, acreage, unit, capacity, beds, deposit, min_days, max_days)):
            return self.write({"errno":1, "errmsg":"params error"})
        try:
            price = int(float(price) * 100)
            deposit = int(float(deposit) * 100)
            house_id = self.db.execute("insert into ih_house_info(hi_user_id,hi_title,hi_price,hi_area_id,hi_address,hi_room_count,hi_acreage,hi_house_unit,hi_capacity,hi_beds,hi_deposit,hi_min_days,hi_max_days) values(%(user_id)s,%(title)s,%(price)s,%(area_id)s,%(address)s,%(room_count)s,%(acreage)s,%(house_unit)s,%(capacity)s,%(beds)s,%(deposit)s,%(min_days)s,%(max_days)s)", user_id=user_id, title=title, price=price, area_id=area_id, address=address, room_count=room_count, acreage=acreage, house_unit=unit, capacity=capacity, beds=beds, deposit=deposit, min_days=min_days, max_days=max_days)
        except Exception as e:
            logging.error(e)
            return self.write({"errno":2, "errmsg":"save house info error"})
        facility = self.json_args.get("facility") 
        if facility:
            sql = "insert into ih_house_facility(hf_house_id,hf_facility_id) values"
            sql_val = []
            val = []
            for facility_id in facility:
                sql_val.append("(%s,%s)")
                val.append(house_id)
                val.append(facility_id)
            sql += ",".join(sql_val)
            val = tuple(val)
            try:
                self.db.execute(sql, *val)
            except Exception as e:
                logging.error(e)
                return self.write({"errno":3, "errmsg":"save facility info erro"})
        self.write({"errno":0, "errmsg":"OK", "house_id":house_id})


class HouseImageHandler(BaseHandler):
    """房屋照片"""
    @require_logined
    def post(self):
        user_id = self.session.data["user_id"]
        house_id = self.get_argument("house_id")
        house_image = self.request.files["house_image"][0]["body"]
        img_name = storage(house_image)
        if not img_name:
            return self.write({"errno":1, "errmsg":"qiniu error"})
        try:
            self.db.execute("insert into ih_house_image(hi_house_id,hi_url) values(%s,%s)", house_id, img_name)
        except Exception as e:
            logging.error(e)
            return self.write({"errno":2, "errmsg":"upload failed"})
        img_url = image_url_prefix + img_name
        self.write({"errno":0, "errmsg":"OK", "url":img_url})