jQuery(document).ready(function($) {
  $("#download-controls").click(function(event) {
    event.preventDefault();
    window.location = "selected/export/xacta/xlsx";
  });

  $("#control-status").change(function() {
    var sid = $(this).data("sid"),
        eid = $(this).data("eid"),
        status = $(this).find('option:selected').text();

    var dataObj = {
      "status": $(this).val(),
      "sid": sid,
      "eid": eid,
    };
    var sid = dataObj.sid;
    $.ajax({
      url: "/controls/" + sid + "/ctrl/_update/",
      type: "POST",
      dataType: "json",
      data: dataObj,
    }).done(function(response) {
      if ($(".usa-alert").length) {
        $(".usa-alert").removeClass("usa-alert--error")
        $(".usa-alert").addClass("usa-alert--success")
        $(".usa-alert").find(".usa-alert__body").html(response.message + ' <b>' + status + '</b>');
      } else {
        $("#focus-area-wrapper").prepend(
          '<div class="usa-alert usa-alert--success margin-1 padding-right-4"><div class="usa-alert__body">' + response.message + ' <b>' + status + '</b></div></div>'
        );
      }
    }).fail(function(jqXHR, textStatus, errorThrown) {
      if ($(".usa-alert").length) {
        $(".usa-alert").removeClass("usa-alert--success")
        $(".usa-alert").addClass("usa-alert--error")
        $(".usa-alert").find(".usa-alert__body").text(textStatus);
      } else {
        $("#focus-area-wrapper").prepend(
          '<div class="usa-alert usa-alert--error margin-1 padding-right-4"><div class="usa-alert__body">' + textStatus + '</div></div>'
        );
      }
    });
  });
});