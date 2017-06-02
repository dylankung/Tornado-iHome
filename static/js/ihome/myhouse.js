$(document).ready(function(){
    // 对于发布房源，只有认证后的用户才可以，所以先判断用户的实名认证状态
    $.get("/api/profile/auth", function(data){
        if ("4101" == data.errno) {
            location.href = "/login.html";
        } else if ("0" == data.errno) {

            // 未认证的用户，在页面中展示 "去认证"的按钮
            if ("" == data.data.real_name || "" == data.data.id_card) {
                $(".auth-warn").show();
                return;
            }
            // 已认证的用户，请求其之前发布的房源信息
            $.get("/api/house/my", function(result){
                $("#houses-list").html(template("houses-list-tmpl", {houses:result.houses})); 
            }); 
        }
    });
})