function hrefBack() {
    history.go(-1);
}

$(document).ready(function() {
    $(".input-daterange").datepicker({
        format: "yyyy-mm-dd",
        startDate: "today",
        language: "zh-CN",
        autoclose: true
    });
    $(".submit-btn").on("click", function(e) {
        location.href = "/orders.html";
    });
})