function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function() {
        setTimeout(function(){
            $('.popup_con').fadeOut('fast',function(){}); 
        },1000) 
    });
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function(){
    $.get("/api/profile", function(data){
        if ("4101" == data.errno) {
            location.href = "/login.html";
        }
        else if ("0" == data.errno) {
            $("#user-name").val(data.data.name);
            if (data.data.avatar) {
                $("#user-avatar").attr("src", data.data.avatar);
            }
        }
    });
    // 为表单的提交事件添加事件函数
    $("#form-avatar").submit(function(e){
        e.preventDefault();
        // ajax请求的配置信息
        var ajax_options = {
            url: "/api/profile/avatar",
            type: "post",
            dataType: "json",
            headers: {
                "X-XSRFToken": getCookie("_xsrf")
            },
            success: function (data) {
                if ("0" == data.errno) {
                    showSuccessMsg();
                    $("#user-avatar").attr("src", data.url);
                } else if ("4101" == data.errno) {
                    document.location.href = "/login.html";
                } else {
                    alert(data.errmsg);
                }
            }
        };
        $(this).ajaxSubmit(ajax_options);
    });
    $("#form-name").submit(function(e){
        e.preventDefault();
        var data = {};
        $(this).serializeArray().map(function(x){data[x.name] = x.value;}); 
        var jsonData = JSON.stringify(data);
        $.ajax({
            url:"/api/profile/name",
            type:"POST",
            data: jsonData, 
            contentType: "application/json",
            dataType: "json",
            headers:{
                "X-XSRFTOKEN":getCookie("_xsrf")
            },
            success: function (data) {
                if ("0" == data.errno) {
                    $(".error-msg").hide();
                    showSuccessMsg();
                } else if ("4001" == data.errno) {
                    $(".error-msg").show();
                } else if ("4101" == data.errno) {
                    location.href = "/login.html";
                }
            }
        });
    })

})