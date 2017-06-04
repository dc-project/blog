/**
 * Created by ysicing on 2017/3/31.
 */
var skip_updates = false;

function init_updater() {
    function update() {
        if (skip_updates) return;

        $.ajax({
            url: location.href,
            cache: true,
            dataType: "html",
            success: function(resp){
                $("#wrapper").find(".main-content").html(resp);
            }
        });
    }

    setInterval(update, 60000);
}

function init_connections_filter() {
    var $content = $("#psdash");
    $content.on("change", "#connections-form select", function () {
        $content.find("#connections-form").submit();
    });
    $content.on("focus", "#connections-form select, #connections-form input", function () {
        skip_updates = true;
    });
    $content.on("blur", "#connections-form select, #connections-form input", function () {
        skip_updates = false;
    });
    $content.on("keypress", "#connections-form input[type='text']", function (e) {
        if (e.which == 13) {
            $content.find("#connections-form").submit();
        }
    });
}


$(document).ready(function() {
    init_connections_filter();
    init_updater();
});