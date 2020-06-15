$(function () {
    var $
})



$("#my_alert").hide();

$("#my_alert").removeClass('alert-success alert-info alert-warning alert-danger').addClass('alert-danger');

// 添加内容
var innerHTML = "<strong>Success!</strong> Have a good time.";
$("#my_alert")[0].innerHTML = innerHTML;

// 出现2s后用slide方式0.5s消失
$("#my_alert").fadeTo(2000, 500).slideUp(500, function(){
    $("#my_alert").hide();
});