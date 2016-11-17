# coding:utf-8

import logging
import constants
import json
import math

from .BaseHandler import BaseHandler
from utils.common import require_logined
from utils.image_storage import storage
from config import image_url_prefix

class HouseAreaHandler(BaseHandler):
    """房屋区域"""
    def get(self):
        try:
            ret = self.redis.get("area_info")
        except Exception as e:
            logging.error(e)
            ret = None
        if ret:
            return self.write(ret)
        try:
            ret = self.db.query("select ai_area_id,ai_name from ih_area_info;")
        except Exception as e:
            logging.error(e)
            return self.write({"errno":1, "errmsg":"get data error"})
        area_data = []
        for area in ret:
            area_data.append(dict(area_id=area["ai_area_id"], name=area["ai_name"]))
        resp = {"errno":0, "errmsg":"OK", "data":area_data}
        try:
            self.redis.setex("area_info", constants.AREA_INFO_REDIS_EXPIRE_SECOND, json.dumps(resp))
        except Exception as e:
            logging.error(e)
        self.write(resp)


class HouseInfoHandler(BaseHandler):
    """单一房屋"""
    def get(self):
        house_id = self.get_argument("id")
        try:
            ret = self.redis.get("hd_%s" % house_id)
        except Exception as e:
            logging.error(e)
            ret = None
        if ret:
            logging.info("hit redis")
            return self.write(ret)
        try:
            ret = self.db.get("select hi_title,hi_price,hi_address,hi_room_count,hi_acreage,hi_house_unit,hi_capacity,hi_beds,hi_deposit,hi_min_days,hi_max_days,up_name,up_avatar from ih_house_info inner join ih_user_profile on hi_user_id=up_user_id where hi_house_id=%s", house_id)
        except Exception as e:
            logging.error(e)
            return self.write({"errno":1, "errmsg":"get data error"})
        if not ret:
            self.write({"errno":2, "errmsg":"no data"})
        house = {
            "hid":house_id,
            "title":ret["hi_title"],
            "price":ret["hi_price"],
            "address":ret["hi_address"],
            "room_count":ret["hi_room_count"],
            "acreage":ret["hi_acreage"],
            "unit":ret["hi_house_unit"],
            "capacity":ret["hi_capacity"],
            "beds":ret["hi_beds"],
            "deposit":ret["hi_deposit"],
            "min_days":ret["hi_min_days"],
            "max_days":ret["hi_max_days"],
            "user_name":ret["up_name"],
            "user_avatar":image_url_prefix + ret["up_avatar"]
        }
        try:
            ret = self.db.query("select hi_url from ih_house_image where hi_house_id=%s", house_id)
        except Exception as e:
            logging.error(e)
            ret = None
        house["img_urls"] = []
        if ret:
            for l in ret:
                house["img_urls"].append(image_url_prefix + l["hi_url"])
        try:
            ret = self.db.query("select hf_facility_id from ih_house_facility where hf_house_id=%s", house_id)
        except Exception as e:
            logging.error(e)
            ret = None
        house["facilities"] = []
        if ret:
            for l in ret:
                house["facilities"].append(l["hf_facility_id"])
        resp = {"errno":0, "errmsg":"OK", "house":house}
        try:
            self.redis.setex("hd_%s" % house_id, constants.HOUSE_DETAIL_REDIS_EXPIRE_SECOND, json.dumps(resp))
        except Exception as e:
            logging.error(e)
        self.write(resp)


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
            self.db.execute("insert into ih_house_image(hi_house_id,hi_url) values(%s,%s);update ih_house_info set hi_index_image_url=%s where hi_house_id=%s and hi_index_image_url is null;", house_id, img_name, img_name, house_id)
        except Exception as e:
            logging.error(e)
            return self.write({"errno":2, "errmsg":"upload failed"})
        img_url = image_url_prefix + img_name
        self.write({"errno":0, "errmsg":"OK", "url":img_url})


class MyHousesHandler(BaseHandler):
    """我的房源"""
    @require_logined
    def get(self):
        user_id = self.session.data["user_id"]
        try:
            ret = self.db.query("select a.hi_house_id,a.hi_title,a.hi_price,a.hi_ctime,b.ai_name,a.hi_index_image_url from ih_house_info a left join ih_area_info b on a.hi_area_id=b.ai_area_id where a.hi_user_id=%s;", user_id)
        except Exception as e:
            logging.error(e)
            return self.write({"errno":1, "errmsg":"get data erro"})
        houses = []
        if ret:
            for l in ret:
                house = {
                    "house_id":l["hi_house_id"],
                    "title":l["hi_title"],
                    "price":l["hi_price"],
                    "ctime":l["hi_ctime"].strftime("%Y-%m-%d"),
                    "area_name":l["ai_name"],
                    "img_url":image_url_prefix + l["hi_index_image_url"] if l["hi_index_image_url"] else ""
                }
                houses.append(house)
        self.write({"errno":0, "errmsg":"OK", "houses":houses})


class IndexHandler(BaseHandler):
    """主页信息"""
    def get(self):
        try:
            ret = self.redis.get("home_page_data")
        except Exception as e:
            logging.error(e)
            ret = None
        if ret:
            return self.write(ret)
        try:
            house_ret = self.db.query("select distinct a.hi_house_id,a.hi_title,a.hi_order_count,a.hi_index_image_url from ih_house_info a inner join ih_house_image b on a.hi_house_id=b.hi_house_id order by a.hi_order_count desc limit %s;" % constants.HOME_PAGE_MAX_HOUSES)
        except Exception as e:
            logging.error(e)
            return self.write({"errno":1, "errmsg":"get data error"})
        if not house_ret:
            return self.write({"errno":2, "errmsg":"no data"})
        houses = []
        for l in house_ret:
            if not l["hi_index_image_url"]:
                continue
            house = {
                "house_id":l["hi_house_id"],
                "title":l["hi_title"],
                "img_url": image_url_prefix + l["hi_index_image_url"]
            }
            houses.append(house)
        try:
            area_ret = self.db.query("select ai_area_id,ai_name from ih_area_info")
        except Exception as e:
            logging.error(e)
            area_ret = None
        areas = []
        if area_ret:
            for area in area_ret:
                areas.append(dict(area_id=area["ai_area_id"], name=area["ai_name"]))
        resp = dict(errno=0, errmsg="OK", houses=houses, areas=areas)
        try:
            self.redis.setex("home_page_data", constants.HOME_PAGE_DATA_REDIS_EXPIRE_SECOND, json.dumps(resp))
        except Exception as e:
            logging.error(e)
        self.write(resp)


class HouseListHandler(BaseHandler):
    """房屋列表信息"""
    def get(self):
        area_id = self.get_argument("aid", "")
        start_date = self.get_argument("sd", "")
        end_date = self.get_argument("ed", "")
        sort_key = self.get_argument("sk", "new")
        page = self.get_argument("p", "1")

        try:
            redis_key = "hs_%s_%s_%s_%s" % (area_id, start_date, end_date, sort_key)
            ret = self.redis.hget(redis_key, page)
        except Exception as e:
            logging.error(e)
        if ret:
            logging.info("hit redis")
            return self.write(ret)

        page = int(page)

        sql_where_li = []
        sql_params = {}

        if area_id:
            sql_where_li.append("hi_area_id=%(area_id)s")
            sql_params["area_id"] = int(area_id)

        if start_date and end_date:
            sql_where_li.append("((oi_begin_date is null and oi_end_date is null) or not (oi_begin_date<%(end_date)s and oi_end_date>%(start_date)s))")
            sql_params["start_date"] = start_date
            sql_params["end_date"] = end_date
        elif start_date:
            sql_where_li.append("((oi_begin_date is null and oi_end_date is null) or oi_end_date<%(start_date)s)")
            sql_params["start_date"] = start_date
        elif end_date:
            sql_where_li.append("((oi_begin_date is null and oi_end_date is null) or oi_begin_date<%(end_date)s)")
            sql_params["end_date"] = end_date

        sql_where = " and ".join(sql_where_li)
        if "" != sql_where:
            sql_where = " where " + sql_where

        try:
            logging.debug("select count(*) counts from ih_house_info left join ih_order_info on hi_house_id=oi_house_id" + sql_where)
            ret = self.db.get("select count(*) counts from ih_house_info left join ih_order_info on hi_house_id=oi_house_id" + sql_where, **sql_params)
        except Exception as e:
            logging.error(e)
            return self.write({"errno":1, "errmsg":"get total_page error"})
        if 0 == ret["counts"]:
            return self.write({"errno":0, "errmsg":"OK", "total_page":0, "data":[]})
        total_page = int(math.ceil(float(ret["counts"]) / constants.HOUSE_LIST_PAGE_CAPACITY))
        if page > total_page:
            return self.write({"errno":0, "errmsg":"OK", "total_page":total_page, "data":[]})

        sql = "select hi_house_id,hi_title,hi_price,hi_room_count,hi_order_count,hi_index_image_url,hi_address,up_avatar from ih_house_info left join ih_order_info on hi_house_id=oi_house_id inner join ih_user_profile on hi_user_id=up_user_id"
        sql += sql_where
        sql += " order by "
        if "booking" == sort_key:
            sql += "hi_order_count desc"
        elif "price-inc" == sort_key:
            sql += "hi_price"
        elif "price-des" == sort_key:
            sql += "hi_price desc"
        else:
            sql += "hi_ctime desc"
        if 1 == page:
            sql += " limit %s" % (constants.HOUSE_LIST_PAGE_CAPACITY * constants.HOUSE_LIST_REIDS_CACHED_PAGE)
        else:
            sql += " limit %s,%s" % ((page-1)*constants.HOUSE_LIST_PAGE_CAPACITY, constants.HOUSE_LIST_PAGE_CAPACITY * constants.HOUSE_LIST_REIDS_CACHED_PAGE)
        try:
            logging.debug(sql)
            ret = self.db.query(sql, **sql_params)
        except Exception as e:
            logging.error(e)
            return self.write({"errno":2, "errmsg":"get data error"})
        if not ret:
            return self.write({"errno":0, "errmsg":"OK", "total_page":total_page, "data":[]})
        houses = []
        for l in ret:
            house = {
                "house_id":l["hi_house_id"],
                "title":l["hi_title"],
                "price":l["hi_price"],
                "room_count":l["hi_room_count"],
                "order_count":l["hi_order_count"],
                "address":l["hi_address"],
                "img_url":image_url_prefix + l["hi_index_image_url"] if l["hi_index_image_url"] else "",
                "avatar_url":image_url_prefix + l["up_avatar"] if l["up_avatar"] else ""
            }
            houses.append(house)
        logging.debug(houses)
        page_data = houses[0:constants.HOUSE_LIST_PAGE_CAPACITY]
        self.write({"errno":0, "errmsg":"OK", "total_page":total_page, "data":page_data})
        redis_data = {
            str(page):json.dumps({"errno":0, "errmsg":"OK", "total_page":total_page, "data":page_data})
        }
        i = 1
        while 1:
            page_data = houses[(i*constants.HOUSE_LIST_PAGE_CAPACITY):((i+1)*constants.HOUSE_LIST_PAGE_CAPACITY)]
            if not page_data:
                break
            redis_data[str(page+i)] = json.dumps({"errno":0, "errmsg":"OK", "total_page":total_page, "data":page_data})  
            i += 1

        redis_key = "hs_%s_%s_%s_%s" % (area_id, start_date, end_date, sort_key)
        try:
            self.redis.hmset(redis_key, redis_data)
        except Exception as e:
            logging.error(e)
            return
        try:
            self.redis.expire(redis_key, constants.HOUSE_LIST_REDIS_EXPIRE_SECOND)
        except Exception as e:
            logging.error(e)
            self.redis.delete(redis_key)

  
 


