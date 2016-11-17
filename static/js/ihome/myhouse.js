$(document).ready(function(){
    $.get("/api/profile/auth", function(data){
        if (-1 == data.errno) {
            location.href = "/login.html";
        } else if (0 == data.errno) {
            if ("" == data.data.real_name || "" == data.data.id_card) {
                $(".auth-warn").show();
                return;
            }
            $.get("/api/house/my", function(result){
                $("#houses-list").html(template("houses-list-tmpl", {houses:result.houses})); 
            }); 
        }
    });
})