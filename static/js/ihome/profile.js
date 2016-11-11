function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function() {
        setTimeout(function(){
            $('.popup_con').fadeOut('fast',function(){}); 
        },1000) 
    });
}

$(document).ready(function(){
    $.get("/api/profile", function(data){
        if (-1 == data.errno) {
            location.href = "/view/login.html";
        }
        else if (0 == data.errno) {
            $("#user-name").val(data.data.name);
            if (data.data.avatar) {
                $("#user-avatar").attr("src", data.data.avatar);
            }
        }
    });
    $("#form-avatar").submit(function(){
        $(this).ajaxSubmit(function(data){
            if (0 == data.errno) {
                showSuccessMsg();
                $("#user-avatar").attr("src", data.url);
            }
        });
        return false;
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
            success: function (data) {
                if (0 == data.errno) {
                    $(".error-msg").hide();
                    showSuccessMsg();
                } else if (2 == data.errno) {
                    $(".error-msg").show();
                }
            }
        });
    })

})