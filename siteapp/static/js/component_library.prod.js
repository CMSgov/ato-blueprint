"use strict";jQuery(document).ready(function(a){a("#type_project_change").val()||a("#project_submit_id").prop("disabled",!0);var e=a("#searchbox").val(),t=window.location.href.split("?")[0];a("#keyword").val(e),a("#library-search").submit(function(e){e.preventDefault(),a("#keyword").val(a("#searchbox").val()),a("#library-filters").trigger("change")}),a("#library-filters").change(function(){var e=a(this).serialize().replace(/(?<=([^\?\&\=]+=)([^\&\=]+))(\&\1)/g,","),r=e?t+"?"+e:t;window.location.replace(r)}),a("#type_project_change").change(function(e){var r=a("#type_project_change option:selected").prop("disabled");e.target.value||(r=!0),a("#project_submit_id").prop("disabled",r)})});