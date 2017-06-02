function hrefBack() {
    history.go(-1);
}

// 解析提取url中的查询字符串参数
function decodeQuery(){
    var search = decodeURI(document.location.search);
    return search.replace(/(^\?)/, '').split('&').reduce(function(result, item){
        values = item.split('=');
        result[values[0]] = values[1];
        return result;
    }, {});
}

$(document).ready(function(){
    // 获取详情页面要展示的房屋编号
    var queryData = decodeQuery();
    var houseId = queryData["id"];

    // 获取该房屋的详细信息
    $.get("/api/house/info?id=" + houseId, function(data){
        if ("0" == data.errno) {
            $(".swiper-container").html(template("house-image-tmpl", {img_urls:data.house.img_urls, price:data.house.price}));
            $(".detail-con").html(template("house-detail-tmpl", {house:data.house}));

            // data.user_id为访问页面用户,data.data.user_id为房东
            if (!(data.user_id == data.house.user_id || "f" in queryData)) {
                $(".book-house").attr("href", "/booking.html?hid="+data.house.hid);
                $(".book-house").show();
            }
            var mySwiper = new Swiper ('.swiper-container', {
                loop: true,
                autoplay: 2000,
                autoplayDisableOnInteraction: false,
                pagination: '.swiper-pagination',
                paginationType: 'fraction'
            });
        }
    })
})