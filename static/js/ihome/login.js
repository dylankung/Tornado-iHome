$(document).ready(function() {
    $("#mobile").focus(function(){
        $("#mobile-err").hide();
    });
    $("#password").focus(function(){
        $("#password-err").hide();
    });
    $(".form-login").submit(function(e){
        e.preventDefault();
        mobile = $("#mobile").val();
        passwd = $("#password").val();
        if (!mobile) {
            $("#mobile-err span").html("请填写正确的手机号！");
            $("#mobile-err").show();
            return;
        } 
        if (!passwd) {
            $("#password-err span").html("请填写密码!");
            $("#password-err").show();
            return;
        }
        $.post("/api/login", $(".form-login").serialize(), function(data){
            if (0 == data.errno) {
                location.href = "/";
                return;
            }
            else {
                $("#password-err span").html(data.errmsg);
                $("#password-err").show();
                return;
            }
        }, 'json')
    });
})