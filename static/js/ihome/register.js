function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

// 保存当前页面中展示的图片验证码的编号
var imageCodeId = "";

function generateUUID() {
    var d = new Date().getTime();
    if(window.performance && typeof window.performance.now === "function"){
        d += performance.now(); //use high-precision timer if available
    }
    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = (d + Math.random()*16)%16 | 0;
        d = Math.floor(d/16);
        return (c=='x' ? r : (r&0x3|0x8)).toString(16);
    });
    return uuid;
}

function generateImageCode() {
    var preImageCodeId = imageCodeId;
    // 新的要请求的图片验证码的编号
    imageCodeId = generateUUID();
    $(".image-code img").attr("src", "/api/imagecode?p="+preImageCodeId+"&c="+imageCodeId);
}

function sendSMSCode() {
    $(".phonecode-a").removeAttr("onclick");
    var mobile = $("#mobile").val();
    if (!mobile) {
        $("#mobile-err span").html("请填写正确的手机号！");
        $("#mobile-err").show();
        $(".phonecode-a").attr("onclick", "sendSMSCode();");
        return;
    } 
    var imageCode = $("#imagecode").val();
    if (!imageCode) {
        $("#image-code-err span").html("请填写验证码！");
        $("#image-code-err").show();
        $(".phonecode-a").attr("onclick", "sendSMSCode();");
        return;
    }
    // $.get("/api/smscode", {mobile:mobile, code:imageCode, codeId:imageCodeId},
    //     function(data){
    //         if (0 != data.errno) {
    //             $("#image-code-err span").html(data.errmsg);
    //             $("#image-code-err").show();
    //             if (2 == data.errno || 3 == data.errno) {
    //                 generateImageCode();
    //             }
    //             $(".phonecode-a").attr("onclick", "sendSMSCode();");
    //         }
    //         else {
    //             var $time = $(".phonecode-a");
    //             var duration = 60;
    //             var intervalid = setInterval(function(){
    //                 $time.html(duration + "秒");
    //                 if(duration === 1){
    //                     clearInterval(intervalid);
    //                     $time.html('获取验证码');
    //                     $(".phonecode-a").attr("onclick", "sendSMSCode();");
    //                 }
    //                 duration = duration - 1;
    //             }, 1000, 60);
    //         }
    // }, 'json');
    var req_data = {
        mobile: mobile,
        codeId: imageCodeId,
        code: imageCode,
    };
    $.ajax({
        url: "/api/smscode",  // 对应的接口url
        type: "post",    // 请求方式
        data: JSON.stringify(req_data), // 请求的参数，转换为json字符串
        contentType: "application/json",
        dataType:"json",
        headers:{
            "X-XSRFToken": getCookie("_xsrf")
        },
        success: function (data) {
            if ("0" == data.errno) {
                var duration = 60;
                var interval = setInterval(function () {
                    duration = duration - 1;
                    $(".phonecode-a").html(duration+"秒");
                    if (1 == duration){
                        clearInterval(interval);
                        $(".phonecode-a").html("获取验证码");
                        $(".phonecode-a").attr("onclick", "sendSMSCode()");
                    }
                }, 1000, 60)
            } else {
                $("#phone-code-err>span").html(data.errmsg);
                $("#phone-code-err").show()
                if ("图片验证码过期" == data.errmsg || "图片验证码错误" == data.errmsg) {
                    generateImageCode();
                }
                $(".phonecode-a").attr("onclick", "sendSMSCode()");
            }
        }

    })
}

$(document).ready(function() {
    generateImageCode();
    $("#mobile").focus(function(){
        $("#mobile-err").hide();
    });
    $("#imagecode").focus(function(){
        $("#image-code-err").hide();
    });
    $("#phonecode").focus(function(){
        $("#phone-code-err").hide();
    });
    $("#password").focus(function(){
        $("#password-err").hide();
        $("#password2-err").hide();
    });
    $("#password2").focus(function(){
        $("#password2-err").hide();
    });
    $(".form-register").submit(function(e){
        // 组织浏览器对于表单的默认行为，组织浏览器打包表单数据发送给后端
        e.preventDefault();
        var mobile = $("#mobile").val();
        var phoneCode = $("#phonecode").val();
        var passwd = $("#password").val();
        var passwd2 = $("#password2").val();
        if (!mobile) {
            $("#mobile-err span").html("请填写正确的手机号！");
            $("#mobile-err").show();
            return;
        } 
        if (!phoneCode) {
            $("#phone-code-err span").html("请填写短信验证码！");
            $("#phone-code-err").show();
            return;
        }
        if (!passwd) {
            $("#password-err span").html("请填写密码!");
            $("#password-err").show();
            return;
        }
        if (passwd != passwd2) {
            $("#password2-err span").html("两次密码不一致!");
            $("#password2-err").show();
            return;
        }
        // 提取表单的所有数据,数组类型
        var form_data = $(".form-register").serializeArray();
        // 定义一个js中的对象，用来保存表单数据中的键值对
        var req_data = {};
        // 将数组数据form_data 转换为js中的对象（字典）,保存到req_data中
        form_data.map(function (x) { req_data[x.name] = x.value });
        // 将req_data 转换为json
        var req_json_data = JSON.stringify(req_data);

        // 利用ajax将数据发送到后端
        $.ajax({
            url: "/api/register",
            type: "post",
            contentType: "application/json",
            data: req_json_data,
            dataType: "json",
            headers: {
                "X-XSRFToken": getCookie("_xsrf")
            },
            success: function (data) {
                if ("0" == data.errno) {
                    // 让页面调转到主页
                    document.location.href = "/";
                } else if ("4003" == data.errno ) {
                    $("#mobile-err>span").html(data.errmsg);
                    $("#mobile-err").show();
                } else if ("验证码过期" == data.errmsg || "验证码错误" == data.errmsg) {
                    $("#phone-code-err>span").html(data.errmsg);
                    $("#phone-code-err").show();
                } else if ("4102" == data.errno) {
                    // 4102代表后端session数据保存失败
                    // 让页面调转到登录页面
                    document.location.href = "/login.html";
                }

            }
        });
    });
})