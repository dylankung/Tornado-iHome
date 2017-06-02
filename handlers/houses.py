# coding:utf-8

import logging
import constants
import json
import math

from handlers.base import BaseHandler
from utils.common import require_logined
from utils.image_storage import storage
from utils.response_code import RET
from config import image_url_prefix
from utils.session import Session


class AreaInfoHandler(BaseHandler):
    """房屋区域"""
    def get(self):
        """提供房屋区域信息"""
        # 先查询redis获取缓存数据
        try:
            areas = self.redis.get("area_info")
        except Exception as e:
            logging.error(e)
            areas = None

        # 如果redis中存在，直接将数据返回
        if areas:
            logging.info("hit area info redis")
            return self.write('{"errno":0, "errmsg":"OK", "data":%s}' % areas)

        # 如果redis中不存在，查询mysql数据库
        # 查询数据库，获取城区信息
        try:
            sql = "select ai_area_id as area_id ,ai_name as name from ih_area_info;"
            areas = self.db.query(sql)
        except Exception as e:
            logging.error(e)
            return self.write(dict(errno=RET.DBERR, errmsg="get data error"))
        json_area_data = json.dumps(areas)
        resp = '{"errno":"0", "errmsg":"OK", "data":%s}' % json_area_data
        try:
            self.redis.setex("area_info", constants.AREA_INFO_REDIS_EXPIRE_SECOND, json_area_data)
        except Exception as e:
            logging.error(e)
        self.write(resp)


class HouseInfoHandler(BaseHandler):
    """房屋详细信息"""
    def get(self):
        """获取房屋详情"""
        # 前端在房屋详情页面展示时，如果浏览页面的用户不是该房屋的房东，则展示预定按钮，否则不展示，
        # 所以需要后端返回登录用户的user_id
        # 尝试获取用户登录的信息，若登录，则返回给前端登录用户的user_id，否则返回user_id=-1
        session = Session(self)
        user_id = session.data.get("user_id", "-1")

        # 获取查询的房屋id
        house_id = self.get_argument("id")

        # 校验参数
        if not house_id:
            return self.write(dict(errcode=RET.PARAMERR, errmsg="缺少参数"))

        # 先从redis缓存中获取信息
        try:
            ret = self.redis.get("house_info_%s" % house_id)
        except Exception as e:
            logging.error(e)
            ret = None
        if ret:
            logging.info("hit house info redis")
            return self.write('{"errno":"0", "errmsg":"OK","user_id":%s, "house":%s}' % (user_id, ret))

        # 查询数据库
        sql = "select hi_title,hi_price,hi_address,hi_room_count,hi_acreage,hi_house_unit,hi_capacity,hi_beds," \
              "hi_deposit,hi_min_days,hi_max_days,up_name,up_avatar,hi_user_id from ih_house_info inner join " \
              "ih_user_profile on hi_user_id=up_user_id where hi_house_id=%s"
        try:
            ret = self.db.get(sql, house_id)
        except Exception as e:
            logging.error(e)
            return self.write(dict(errno=RET.DBERR, errmsg="get data error"))

        # 用户查询的可能是不存在的房屋id, 此时ret为None
        if not ret:
            return self.write(dict(errno=RET.NODATA, errmsg="no data"))

        house = {
            "hid": house_id,
            "user_id": ret["hi_user_id"],
            "title": ret["hi_title"],
            "price": ret["hi_price"],
            "address": ret["hi_address"],
            "room_count": ret["hi_room_count"],
            "acreage": ret["hi_acreage"],
            "unit": ret["hi_house_unit"],
            "capacity": ret["hi_capacity"],
            "beds": ret["hi_beds"],
            "deposit": ret["hi_deposit"],
            "min_days": ret["hi_min_days"],
            "max_days": ret["hi_max_days"],
            "user_name": ret["up_name"],
            "user_avatar": image_url_prefix + ret["up_avatar"]
        }

        # 查询房屋的图片信息
        sql = "select hi_url from ih_house_image where hi_house_id=%s"
        try:
            ret = self.db.query(sql, house_id)
        except Exception as e:
            logging.error(e)
            ret = None

        house["img_urls"] = []
        if ret:
            for image in ret:
                house["img_urls"].append(image_url_prefix + image["hi_url"])

        # 查询房屋的基本设施
        sql = "select hf_facility_id from ih_house_facility where hf_house_id=%s"
        try:
            ret = self.db.query(sql, house_id)
        except Exception as e:
            logging.error(e)
            ret = None

        house["facilities"] = []
        if ret:
            for facility in ret:
                house["facilities"].append(facility["hf_facility_id"])

        # 查询评论信息
        sql = "select oi_comment,up_name,up_mobile,oi_utime from ih_order_info inner join ih_user_profile " \
              "on oi_user_id=up_user_id where oi_house_id=%(house_id)s and oi_status=4 and oi_comment is not null " \
              "order by oi_utime desc limit %(limit)s"
        try:
            ret = self.db.query(sql, house_id=house_id, limit=constants.HOUSE_DETAIL_COMMENT_DISPLAY_COUNTS)
        except Exception as e:
            logging.error(e)
            ret = None
        house["comments"] = []
        if ret:
            for l in ret:
                comment = {
                    "comment": l["oi_comment"],
                    "user_name": l["up_name"] if l["up_name"] != l["up_mobile"] else "匿名用户",
                    "ctime": l["oi_utime"].strftime("%Y-%m-%d %H:%M:%S")
                }
                house["comments"].append(comment)

        # 存入到redis中
        json_house = json.dumps(house)
        try:
            self.redis.setex("house_info_%s" % house_id, constants.HOUSE_DETAIL_REDIS_EXPIRE_SECOND, json_house)
        except Exception as e:
            logging.error(e)
        resp = '{"errno":"0", "errmsg":"OK","user_id":%s, "house":%s}' % (user_id, json_house)
        self.write(resp)

    @require_logined
    def post(self):
        """
        房东发布房源信息
        前端发送过来的json数据
        {
            "title":"",
            "price":"",
            "area_id":"1",
            "address":"",
            "room_count":"",
            "acreage":"",
            "unit":"",
            "capacity":"",
            "beds":"",
            "deposit":"",
            "min_days":"",
            "max_days":"",
            "facility":["7","8"]
        }
        """
        user_id = self.session.data["user_id"]  # 用户编号
        title = self.json_args.get("title")  # 房屋名称标题
        price = self.json_args.get("price")  # 房屋单价
        area_id = self.json_args.get("area_id")  # 房屋所属城区的编号
        address = self.json_args.get("address")  # 房屋地址
        room_count = self.json_args.get("room_count")  # 房屋包含的房间数目
        acreage = self.json_args.get("acreage")  # 房屋面积
        unit = self.json_args.get("unit")  # 房屋布局（几室几厅)
        capacity = self.json_args.get("capacity")  # 房屋容纳人数
        beds = self.json_args.get("beds")  # 房屋卧床数目
        deposit = self.json_args.get("deposit")  # 押金
        min_days = self.json_args.get("min_days")  # 最小入住天数
        max_days = self.json_args.get("max_days")  # 最大入住天数

        # 校验传入数据
        if not all((title, price, area_id, address, room_count, acreage, unit, capacity, beds, deposit, min_days,
                    max_days)):
            return self.write(dict(errno=RET.PARAMERR, errmsg="缺少参数"))

        # 前端传过来的单价和押金是以元为单位，转换为分
        try:
            price = int(float(price) * 100)
            deposit = int(float(deposit) * 100)
        except Exception as e:
            return self.write(dict(errno=RET.PARAMERR, errmsg="参数错误"))

        # 保存房屋基本信息数据到数据库
        sql = "insert into ih_house_info(hi_user_id,hi_title,hi_price,hi_area_id,hi_address,hi_room_count,hi_acreage," \
              "hi_house_unit,hi_capacity,hi_beds,hi_deposit,hi_min_days,hi_max_days) values(%(user_id)s,%(title)s," \
              "%(price)s,%(area_id)s,%(address)s,%(room_count)s,%(acreage)s,%(house_unit)s,%(capacity)s,%(beds)s," \
              "%(deposit)s,%(min_days)s,%(max_days)s)"
        try:
            # 对于insert语句，execute方法会返回最后一个自增id
            house_id = self.db.execute(sql, user_id=user_id, title=title, price=price, area_id=area_id, address=address,
                                       room_count=room_count, acreage=acreage, house_unit=unit, capacity=capacity,
                                       beds=beds, deposit=deposit, min_days=min_days, max_days=max_days)
        except Exception as e:
            logging.error(e)
            return self.write(dict(errno=RET.DBERR, errmsg="save data error"))

        # 处理房屋的设施信息，保存数据到设施信息数据库表中
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
                try:
                    self.db.execute("delete from ih_house_info where hi_house_id=%s", house_id)
                except Exception as e:
                    logging.error(e)
                    return self.write(dict(errno=RET.DBERR, errmsg="delete fail"))
                else:
                    return self.write(dict(errno=RET.DBERR, errmsg="no data save"))
                    return self.write({"errno":3, "errmsg":"save facility info erro"})

        self.write(dict(errno=RET.OK, errmsg="OK", house_id=house_id))


class HouseImageHandler(BaseHandler):
    """房屋照片"""
    @require_logined
    def post(self):
        """房东上传房屋照片"""
        # 获取要保存的房屋id与照片
        house_id = self.get_argument("house_id")
        house_image = self.request.files["house_image"][0]["body"]
        # 调用我们封装好的上传七牛的storage方法上传图片
        img_name = storage(house_image)
        if not img_name:
            return self.write({"errno": RET.THIRDERR, "errmsg": "qiniu error"})
        try:
            # 保存图片路径到数据库ih_house_image表,并且设置房屋的主图片(ih_house_info中的hi_index_image_url）
            # 我们将用户上传的第一张图片作为房屋的主图片
            sql = "insert into ih_house_image(hi_house_id,hi_url) values(%s,%s);" \
                  "update ih_house_info set hi_index_image_url=%s " \
                  "where hi_house_id=%s and hi_index_image_url is null;"
            self.db.execute(sql, house_id, img_name, img_name, house_id)
        except Exception as e:
            logging.error(e)
            return self.write({"errno": RET.DBERR, "errmsg": "upload failed"})
        img_url = image_url_prefix + img_name
        self.write({"errno": RET.OK, "errmsg": "OK", "url": img_url})


class MyHousesHandler(BaseHandler):
    """我的房源"""
    @require_logined
    def get(self):
        """获取房东发布的房源信息条目"""
        user_id = self.session.data["user_id"]

        # 查询数据库,获取房屋基本数据
        try:
            sql = "select a.hi_house_id,a.hi_title,a.hi_price,a.hi_ctime,b.ai_name,a.hi_index_image_url " \
                  "from ih_house_info a left join ih_area_info b on a.hi_area_id=b.ai_area_id where a.hi_user_id=%s;"
            ret = self.db.query(sql, user_id)
        except Exception as e:
            logging.error(e)
            return self.write({"errno": RET.DBERR, "errmsg": "get data error"})
        houses = []
        if ret:
            for l in ret:
                house = {
                    "house_id": l["hi_house_id"],
                    "title": l["hi_title"],
                    "price": l["hi_price"],
                    "ctime": l["hi_ctime"].strftime("%Y-%m-%d"),
                    "area_name": l["ai_name"],
                    "img_url": image_url_prefix + l["hi_index_image_url"] if l["hi_index_image_url"] else ""
                }
                houses.append(house)
        self.write({"errno": RET.OK, "errmsg": "OK", "houses": houses})


class IndexHandler(BaseHandler):
    """主页信息"""
    def get(self):
        """获取主页幻灯片展示的房屋基本信息"""
        # 从缓存中尝试获取数据
        try:
            ret = self.redis.get("home_page_data")
        except Exception as e:
            logging.error(e)
            ret = None
        if ret:
            json_houses = ret
        else:
            try:
                # 查询数据库，返回房屋订单数目最多的5条数据(房屋订单通过hi_order_count来表示）
                sql = "select hi_house_id,hi_title,hi_order_count,hi_index_image_url from ih_house_info " \
                    "order by hi_order_count desc limit %s;"
                house_ret = self.db.query(sql, constants.HOME_PAGE_MAX_HOUSES)
            except Exception as e:
                logging.error(e)
                return self.write({"errno": RET.DBERR, "errmsg": "get data error"})
            if not house_ret:
                return self.write({"errno": RET.NODATA, "errmsg": "no data"})
            houses = []
            for l in house_ret:
                if not l["hi_index_image_url"]:
                    continue
                house = {
                    "house_id": l["hi_house_id"],
                    "title": l["hi_title"],
                    "img_url": image_url_prefix + l["hi_index_image_url"]
                }
                houses.append(house)
            json_houses = json.dumps(houses)
            try:
                self.redis.setex("home_page_data", constants.HOME_PAGE_DATA_REDIS_EXPIRE_SECOND, json_houses)
            except Exception as e:
                logging.error(e)

        # 返回首页城区数据
        try:
            ret = self.redis.get("area_info")
        except Exception as e:
            logging.error(e)
            ret = None
        if ret:
            json_areas = ret
        else:
            try:
                area_ret = self.db.query("select ai_area_id,ai_name from ih_area_info")
            except Exception as e:
                logging.error(e)
                area_ret = None
            areas = []
            if area_ret:
                for area in area_ret:
                    areas.append(dict(area_id=area["ai_area_id"], name=area["ai_name"]))
            json_areas = json.dumps(areas)
            try:
                self.redis.setex("area_info", constants.AREA_INFO_REDIS_EXPIRE_SECOND, json_areas)
            except Exception as e:
                logging.error(e)
        resp = '{"errno":"0", "errmsg":"OK", "houses":%s, "areas":%s}' % (json_houses, json_areas)
        self.write(resp)


class HouseListHandler(BaseHandler):
    """房屋列表信息"""
    def get(self):
        """获取房屋分页数据 未使用缓存版本"""
        # 获取参数
        area_id = self.get_argument("aid", "")
        start_date = self.get_argument("sd", "")
        end_date = self.get_argument("ed", "")
        sort_key = self.get_argument("sk", "new")
        page = self.get_argument("p", "1")

        # 查询数据库获取数据
        sql = "select distinct a.hi_house_id,a.hi_price,a.hi_title,a.hi_index_image_url,a.hi_room_count,a.hi_address," \
              "a.hi_order_count,b.up_avatar  from ih_house_info a inner join ih_user_profile b " \
              "on a.hi_user_id=b.up_user_id left join ih_order_info c on a.hi_house_id=c.oi_house_id"
        sql_total_page = "select count(distinct a.hi_house_id) as counts from ih_house_info a inner join " \
                         "ih_user_profile b on a.hi_user_id=b.up_user_id left join ih_order_info c " \
                         "on a.hi_house_id=c.oi_house_id"

        # 存放可能的筛选条件
        sql_where_li = []

        # 存放动态绑定需要的参数值
        sql_params = {}

        if area_id:
            sql_where_li.append("hi_area_id=%(area_id)s")
            sql_params["area_id"] = int(area_id)

        # 早先版本的日期筛选条件有错误，此处注释的为错误的版本
        # if start_date and end_date:
        #     sql_where.append("(oi_start_date is null or oi_end_date is null or c.oi_start_date>%(end_date)s "
        #                      "or c.oi_end_date < %(start_date)s)")
        #     sql_value["start_date"] = start_date
        #     sql_value["end_date"] = end_date
        # elif start_date:
        #     sql_where.append("(oi_start_date is null or oi_end_date is null or c.oi_end_date < %(start_date)s)")
        #     sql_value["start_date"] = start_date
        # elif end_date:
        #     sql_where.append("(oi_start_date is null or oi_end_date is null or c.oi_start_date>%(end_date)s)")
        #     sql_value["end_date"] = end_date

        if start_date and end_date:
            sql_where_li.append(" a.hi_house_id not in (select oi_house_id from ih_order_info "
                                "where oi_begin_date<=%(end_date)s and oi_end_date>=%(start_date)s)")
            sql_params["start_date"] = start_date
            sql_params["end_date"] = end_date
        elif start_date:
            sql_where_li.append(" a.hi_house_id not in (select oi_house_id from ih_order_info "
                                "where oi_end_date>=%(start_date)s)")
            sql_params["start_date"] = start_date
        elif end_date:
            sql_where_li.append(" a.hi_house_id not in (select oi_house_id from ih_order_info "
                                "where oi_begin_date<=%(end_date)s)")
            sql_params["end_date"] = end_date

        if sql_where_li:
            sql += " where "
            sql += " and ".join(sql_where_li)
            sql_total_page += " where "
            sql_total_page += " and ".join(sql_where_li)

        # 查询总页数
        try:
            logging.debug(sql_total_page)
            ret = self.db.get(sql_total_page, **sql_params)
        except Exception as e:
            logging.error(e)
            ret = None
            total_page = -1

        # 总数为0代表无数据
        if 0 == ret["counts"]:
            return self.write({"errno": RET.OK, "errmsg": "OK", "total_page": 0, "data": []})

        page = int(page)
        if -1 != total_page:
            total_page = int(math.ceil(float(ret["counts"]) / constants.HOUSE_LIST_PAGE_CAPACITY))
            # 如果用户要查询的页数大于总页数，直接返回
            if page > total_page:
                return self.write({"errno": RET.OK, "errmsg": "OK", "total_page": total_page, "data": []})

        sql += " order by "
        if "booking" == sort_key:
            sql += "a.hi_order_count desc"
        elif "price-inc" == sort_key:
            sql += "a.hi_price"
        elif "price-des" == sort_key:
            sql += "a.hi_price desc"
        else:
            sql += "a.hi_ctime desc"

        if 1 == page:
            sql += (" limit %s" % constants.HOUSE_LIST_PAGE_CAPACITY )
        else:
            sql += (" limit %s,%s" % ((page-1)*constants.HOUSE_LIST_PAGE_CAPACITY, constants.HOUSE_LIST_PAGE_CAPACITY))

        try:
            logging.debug(sql)
            ret = self.db.query(sql, **sql_params)
        except Exception as e:
            logging.error(e)
            return self.write({"errno": RET.DBERR, "errmsg": "get data error"})

        if not ret:
            return self.write({"errno": 0, "errmsg": "OK", "total_page": total_page, "data": []})
        houses = []
        for l in ret:
            house = {
                "house_id": l["hi_house_id"],
                "title": l["hi_title"],
                "price": l["hi_price"],
                "room_count": l["hi_room_count"],
                "order_count": l["hi_order_count"],
                "address": l["hi_address"],
                "img_url": image_url_prefix + l["hi_index_image_url"] if l["hi_index_image_url"] else "",
                "avatar_url": image_url_prefix + l["up_avatar"] if l["up_avatar"] else ""
            }
            houses.append(house)
        self.write({"errno": RET.OK, "errmsg": "OK", "total_page": total_page, "data": houses})


class HouseListRedisHandler(BaseHandler):
    """房屋列表信息"""
    def get(self):
        """获取房屋分页数据 使用缓存版本"""
        # 获取参数
        area_id = self.get_argument("aid", "")
        start_date = self.get_argument("sd", "")
        end_date = self.get_argument("ed", "")
        sort_key = self.get_argument("sk", "new")
        page = self.get_argument("p", "1")

        # 先读取redis缓存数据
        try:
            redis_key = "houses_%s_%s_%s_%s" % (area_id, start_date, end_date, sort_key)
            ret = self.redis.hget(redis_key, page)
        except Exception as e:
            logging.error(e)
            ret = None
        if ret:
            logging.info("hit houses list redis")
            return self.write(ret)

        # 查询数据库获取数据
        sql = "select distinct a.hi_house_id,a.hi_price,a.hi_title,a.hi_index_image_url,a.hi_room_count,a.hi_address," \
              "a.hi_order_count,b.up_avatar  from ih_house_info a inner join ih_user_profile b " \
              "on a.hi_user_id=b.up_user_id left join ih_order_info c on a.hi_house_id=c.oi_house_id"
        sql_total_page = "select count(distinct a.hi_house_id) as counts from ih_house_info a inner join " \
                         "ih_user_profile b on a.hi_user_id=b.up_user_id left join ih_order_info c " \
                         "on a.hi_house_id=c.oi_house_id"

        # 存放可能的筛选条件
        sql_where_li = []

        # 存放动态绑定需要的参数值
        sql_params = {}

        if area_id:
            sql_where_li.append("hi_area_id=%(area_id)s")
            sql_params["area_id"] = int(area_id)

        # 早先版本的日期筛选条件有错误，此处注释的为错误的版本
        # if start_date and end_date:
        #     sql_where.append("(oi_start_date is null or oi_end_date is null or c.oi_start_date>%(end_date)s "
        #                      "or c.oi_end_date < %(start_date)s)")
        #     sql_value["start_date"] = start_date
        #     sql_value["end_date"] = end_date
        # elif start_date:
        #     sql_where.append("(oi_start_date is null or oi_end_date is null or c.oi_end_date < %(start_date)s)")
        #     sql_value["start_date"] = start_date
        # elif end_date:
        #     sql_where.append("(oi_start_date is null or oi_end_date is null or c.oi_start_date>%(end_date)s)")
        #     sql_value["end_date"] = end_date

        if start_date and end_date:
            sql_where_li.append(" a.hi_house_id not in (select oi_house_id from ih_order_info "
                                "where oi_begin_date<=%(end_date)s and oi_end_date>=%(start_date)s)")
            sql_params["start_date"] = start_date
            sql_params["end_date"] = end_date
        elif start_date:
            sql_where_li.append(" a.hi_house_id not in (select oi_house_id from ih_order_info "
                                "where oi_end_date>=%(start_date)s)")
            sql_params["start_date"] = start_date
        elif end_date:
            sql_where_li.append(" a.hi_house_id not in (select oi_house_id from ih_order_info "
                                "where oi_begin_date<=%(end_date)s)")
            sql_params["end_date"] = end_date

        if sql_where_li:
            sql += " where "
            sql += " and ".join(sql_where_li)
            sql_total_page += " where "
            sql_total_page += " and ".join(sql_where_li)

        # 查询总页数
        try:
            logging.debug(sql_total_page)
            ret = self.db.get(sql_total_page, **sql_params)
        except Exception as e:
            logging.error(e)
            ret = None
            total_page = -1
        else:
            # 总数为0代表无数据
            if 0 == ret["counts"]:
                return self.write({"errno": RET.OK, "errmsg": "OK", "total_page": 0, "data": []})

            page = int(page)
            total_page = int(math.ceil(float(ret["counts"]) / constants.HOUSE_LIST_PAGE_CAPACITY))
            # 如果用户要查询的页数大于总页数，直接返回
            if page > total_page:
                return self.write({"errno": RET.OK, "errmsg": "OK", "total_page": total_page, "data": []})

        sql += " order by "
        if "booking" == sort_key:
            sql += "a.hi_order_count desc"
        elif "price-inc" == sort_key:
            sql += "a.hi_price"
        elif "price-des" == sort_key:
            sql += "a.hi_price desc"
        else:
            sql += "a.hi_ctime desc"

        if 1 == page:
            sql += (" limit %s" % (constants.HOUSE_LIST_PAGE_CAPACITY * constants.HOUSE_LIST_REDIS_CACHED_PAGE))
        else:
            sql += (" limit %s,%s" % ((page-1) * constants.HOUSE_LIST_PAGE_CAPACITY,
                                      constants.HOUSE_LIST_PAGE_CAPACITY * constants.HOUSE_LIST_REDIS_CACHED_PAGE))

        try:
            logging.debug(sql)
            ret = self.db.query(sql, **sql_params)
        except Exception as e:
            logging.error(e)
            return self.write({"errno": RET.DBERR, "errmsg": "get data error"})

        if not ret:
            return self.write({"errno": RET.OK, "errmsg": "OK", "total_page": total_page, "data": []})
        houses = []
        for l in ret:
            house = {
                "house_id": l["hi_house_id"],
                "title": l["hi_title"],
                "price": l["hi_price"],
                "room_count": l["hi_room_count"],
                "order_count": l["hi_order_count"],
                "address": l["hi_address"],
                "img_url": image_url_prefix + l["hi_index_image_url"] if l["hi_index_image_url"] else "",
                "avatar_url": image_url_prefix + l["up_avatar"] if l["up_avatar"] else ""
            }
            houses.append(house)

        redis_data = {}
        # 切片拿到的每页数据
        i = 0
        while True:
            page_data = houses[(i*constants.HOUSE_LIST_PAGE_CAPACITY):((i+1)*constants.HOUSE_LIST_PAGE_CAPACITY)]
            if not page_data:
                break
            redis_data[str(page+i)] = json.dumps({"errno": RET.OK, "errmsg": "OK", "total_page": total_page,
                                                  "data": page_data})
            i += 1

        redis_key = "houses_%s_%s_%s_%s" % (area_id, start_date, end_date, sort_key)

        # 设置redis的hash数据
        try:
            self.redis.hmset(redis_key, redis_data)
        except Exception as e:
            logging.error(e)
            return

        # 设置redis数据的有效期
        try:
            self.redis.expire(redis_key, constants.HOUSE_LIST_REDIS_EXPIRE_SECOND)
        except Exception as e:
            logging.error(e)
            self.redis.delete(redis_key)

        self.write(redis_data[str(page)])

 


