$(document).ready(function () {
   $("#register-form").submit(function(e){
        // e.preventDefault();
        if ($("#passwd1").val() != $("#passwd2").val()) {
            alert("not equal!");
            $("#passwd1").val("");
            $("#passwd2").val("");
            e.preventDefault();
            return;
        } 
        else {
            var form_data = $("#register-form").serialize(); 
            // _xsrf = get_cookie("_xsrf") 
            // form_data = {
            //     _xsrf:_xsrf,
            //     mobile: '18511111111',
            //     mobile1: '18511111111',
            //     mobile2: '18511111111',
            // }
 
            // json_data = JSON.stringify(form_data)
            $.post("/register", form_data, function (data) {
                var obj = JSON.parse(data);
                if (obj.status == "E01") {
                    alert("mobile error!");
                    return;
                } else if ("00" == obj.status) {
                    location.href="/"; 
                }
            })
            // $.ajax({
            //     type: 'POST',
            //     url: "/register",
            //     headers: {
            //         "X-XSRFToken":_xsrf
            //     },
            //     data:json_data
            // }).done(function(data) { 
            //     alert(data);
            // });
        }
    }); 

   function get_cookie(name) {
        r = document.cookie.match("\\b"+"_xsrf"+"=([^;]*)\\b")
        return r ? r[1] : undefined
   }
})