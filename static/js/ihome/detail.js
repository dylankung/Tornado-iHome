function hrefBack() {
    history.go(-1);
}

function decodeQuery(){
    var search = decodeURI(document.location.search);
    return search.replace(/(^\?)/, '').split('&').reduce(function(result, item){
        values = item.split('=');
        result[values[0]] = values[1];
        return result;
    }, {});
}

$(document).ready(function(){
    var queryData = decodeQuery();
    var houseId = queryData["id"];
    $.get("/api/house/info?id=" + houseId, function(data){
        if (0 == data.errno) {
            $(".swiper-container").html(template("house-image-tmpl", {img_urls:data.house.img_urls, price:data.house.price}));
            $(".detail-con").html(template("house-detail-tmpl", {house:data.house}));
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
            })
        }
    })
})