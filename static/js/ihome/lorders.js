$(document).ready(function(){
    $.get("/api/order/my?role=landlord", function(data){
        if (0 == data.errno) {
            $(".orders-list").html(template("orders-list-tmpl", {orders:data.orders}));
        }
    });
});