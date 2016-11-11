$(document).ready(function(){
    $.get("/api/profile/auth", function(data){
        if (-1 == data.errno) {
            location.href = "/login.html";
        } else if (0 == data.errno) {
            $.get("/api/house/my", function(result){
                $("#houses-list").render("houses-list-tmpl", {houses:result.houses}); 
            }); 
        } else {
            $(".auth-warn").show();
        }
    });
})